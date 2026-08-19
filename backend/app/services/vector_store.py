import os
import json
import math
import hashlib
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import boto3

from app.config import settings
from app.utils.logger import logger

class VectorStore:
    _data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    _store_file = os.path.join(_data_dir, "vector_store.json")

    @classmethod
    def _initialize_store(cls):
        """
        Ensures the data directory exists and returns loaded store contents.
        """
        os.makedirs(cls._data_dir, exist_ok=True)
        if not os.path.exists(cls._store_file):
            with open(cls._store_file, "w", encoding="utf-8") as f:
                json.dump({"sources": {}, "chunks": []}, f)
            return {"sources": {}, "chunks": []}
            
        try:
            with open(cls._store_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read vector store JSON, resetting: {str(e)}")
            return {"sources": {}, "chunks": []}

    @classmethod
    def _save_store(cls, data: Dict[str, Any]):
        """
        Saves the store contents back to the local JSON file.
        """
        os.makedirs(cls._data_dir, exist_ok=True)
        try:
            with open(cls._store_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")

    @classmethod
    async def get_embedding(cls, text: str) -> List[float]:
        """
        Generates 1536-dimensional float embedding vector.
        Uses AWS Bedrock if configured; falls back to a deterministic hashing projection vector in Dev Mode.
        """
        if settings.is_aws_configured:
            try:
                # Resolve Bedrock client
                client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                
                body = json.dumps({"inputText": text})
                response = client.invoke_model(
                    modelId="amazon.titan-embed-text-v1",
                    contentType="application/json",
                    accept="application/json",
                    body=body
                )
                response_body = json.loads(response.get("body").read())
                embedding = response_body.get("embedding")
                if embedding:
                    return embedding
            except Exception as e:
                logger.error(f"Failed to generate Bedrock embedding, falling back to local mock: {str(e)}")
                
        # --- Local Dev Fallback (Deterministic Hash Bag of Words projection) ---
        dimension = 1536
        vector = [0.0] * dimension
        # Normalize and find word tokens
        words = re.findall(r'\w+', text.lower())
        if not words:
            return vector
            
        for word in words:
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            index = h % dimension
            sign = 1 if (h % 2 == 0) else -1
            vector[index] += sign * 1.0
            
        # Normalize vector magnitude to unit length (L2 norm)
        sq_sum = sum(x*x for x in vector)
        if sq_sum > 0:
            mag = math.sqrt(sq_sum)
            vector = [x / mag for x in vector]
            
        return vector

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """
        Calculates cosine similarity between two float vectors.
        """
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1))
        n2 = math.sqrt(sum(b * b for b in v2))
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    @classmethod
    def get_sources(cls) -> List[Dict[str, Any]]:
        """
        Retrieves all registered knowledge sources.
        """
        store = cls._initialize_store()
        return list(store.get("sources", {}).values())

    @classmethod
    def update_source_status(cls, url: str, status: str, message: Optional[str] = None, pages_count: int = 0):
        """
        Updates status details of a specific URL source.
        """
        store = cls._initialize_store()
        store["sources"][url] = {
            "url": url,
            "status": status,
            "message": message,
            "pages_count": pages_count,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        cls._save_store(store)

    @classmethod
    def delete_source(cls, url: str):
        """
        Deletes a source URL and removes all its indexed text chunks.
        """
        store = cls._initialize_store()
        # Remove source details
        store["sources"].pop(url, None)
        # Remove all chunks associated with this source URL
        # We delete if chunk's source_url starts with or matches this URL (covers crawling scope)
        initial_count = len(store["chunks"])
        store["chunks"] = [
            chunk for chunk in store["chunks"] 
            if chunk["source_url"] != url and not chunk["source_url"].startswith(url)
        ]
        removed_count = initial_count - len(store["chunks"])
        logger.info(f"Removed source '{url}' and deleted {removed_count} chunks from index")
        cls._save_store(store)

    @classmethod
    async def add_chunks(cls, url: str, pages: List[Dict[str, Any]], chunk_size: int = 800, overlap: int = 150):
        """
        Splits text, generates embeddings, and indexes them in the local vector store.
        """
        # First, clear any existing chunks for this base URL to prevent duplicate index bloat
        cls.delete_source(url)
        
        store = cls._initialize_store()
        total_chunks = 0

        # Mark source as processing
        store["sources"][url] = {
            "url": url,
            "status": "processing",
            "message": None,
            "pages_count": len(pages),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        cls._save_store(store)

        try:
            for page in pages:
                page_url = page["url"]
                title = page["title"]
                text = page["text"]
                
                # Split page text into sliding window chunks
                chunks = []
                if text:
                    start = 0
                    while start < len(text):
                        end = start + chunk_size
                        chunk_text = text[start:end].strip()
                        if chunk_text:
                            chunks.append(chunk_text)
                        start += (chunk_size - overlap)

                for idx, chunk_text in enumerate(chunks):
                    # Generate embedding
                    embedding = await cls.get_embedding(chunk_text)
                    
                    chunk_obj = {
                        "chunk_id": f"{urlparse(page_url).netloc}-{hashlib.md5(chunk_text.encode('utf-8')).hexdigest()[:8]}",
                        "source_url": page_url,
                        "page_title": title,
                        "text": chunk_text,
                        "embedding": embedding
                    }
                    store["chunks"].append(chunk_obj)
                    total_chunks += 1
            
            # Update source details as successful
            store["sources"][url] = {
                "url": url,
                "status": "success",
                "message": None,
                "pages_count": len(pages),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"Successfully processed URL '{url}': Indexed {len(pages)} pages, {total_chunks} chunks")
        except Exception as e:
            logger.error(f"Failed to process/index URL '{url}': {str(e)}")
            store["sources"][url] = {
                "url": url,
                "status": "failed",
                "message": str(e),
                "pages_count": 0,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            raise e
        finally:
            cls._save_store(store)

    @classmethod
    async def query_similarity(cls, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Queries the vector index for the top K closest chunks using Cosine Similarity.
        """
        store = cls._initialize_store()
        chunks = store.get("chunks", [])
        if not chunks:
            return []

        # Generate query embedding
        query_emb = await cls.get_embedding(query)
        
        matches = []
        for chunk in chunks:
            similarity = cls._cosine_similarity(query_emb, chunk["embedding"])
            # In mock embedding mode, a lower threshold helps capture overlap
            # For Titan embeddings, similarity values are typically tighter (0.3+ threshold)
            min_threshold = 0.05 if not settings.is_aws_configured else 0.25
            
            if similarity >= min_threshold:
                matches.append({
                    "chunk_id": chunk["chunk_id"],
                    "source_url": chunk["source_url"],
                    "page_title": chunk["page_title"],
                    "text": chunk["text"],
                    "similarity": similarity
                })
        
        # Sort in descending order of similarity
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches[:top_k]
