import os
import json
import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"
        self._model = None
        self.dimension = 384  # Dimension of all-MiniLM-L6-v2
        self.index_path = os.path.join(settings.VECTOR_DIR, "index.faiss")
        self.metadata_path = os.path.join(settings.VECTOR_DIR, "metadata.json")
        
        # Initialize Gemini API
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            logger.info("Gemini API initialized successfully.")
        else:
            logger.warning("GEMINI_API_KEY is not set. Gemini calls will fall back to local mock responses.")

        self.index = None
        self.chunks: List[Dict[str, Any]] = []
        self._load_index()

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
            self._model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer model loaded.")
        return self._model

    def _load_index(self):
        """Loads FAISS index and metadata from disk if they exist, otherwise creates a new one."""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                logger.info(f"Loaded existing FAISS index with {len(self.chunks)} chunks.")
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                self.chunks = []
                logger.info("Initialized new empty FAISS index.")
        except Exception as e:
            logger.error(f"Error loading index: {e}. Reinitializing.")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks = []

    def _save_index(self):
        """Saves FAISS index and metadata to disk."""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved FAISS index with {len(self.chunks)} chunks to disk.")
        except Exception as e:
            logger.error(f"Error saving index to disk: {e}")

    def add_documents(self, text: str, source: str, title: str, category: str):
        """Chunks a text document, generates embeddings, and adds them to FAISS."""
        if not text.strip():
            return

        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        split_texts = splitter.split_text(text)
        
        if not split_texts:
            return

        # Compute embeddings
        embeddings = self.model.encode(split_texts)
        embeddings_np = np.array(embeddings).astype('float32')

        # Add to index
        start_idx = len(self.chunks)
        self.index.add(embeddings_np)

        # Add metadata
        for i, chunk_text in enumerate(split_texts):
            self.chunks.append({
                "id": start_idx + i,
                "text": chunk_text,
                "source": source,
                "title": title,
                "category": category
            })

        self._save_index()

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Queries the vector index for similar chunks."""
        if not self.chunks or self.index.ntotal == 0:
            return []

        # Encode query
        query_vector = self.model.encode([query])
        query_vector_np = np.array(query_vector).astype('float32')

        # Search index
        k_actual = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_vector_np, k_actual)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(distances[0][i])
            results.append(chunk)

        # Sort results (lower L2 distance is better)
        results.sort(key=lambda x: x["score"])
        return results

    def clear_index(self):
        """Clears the FAISS index and metadata."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        self._save_index()
        logger.info("FAISS index and metadata cleared.")

    def ask_gemini(self, query: str, context: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Sends the retrieved context and question to Gemini. Falls back to mock responses if key is missing."""
        system_prompt = (
            "You are HYBO, the official AI-powered Smart City Assistant for Hyderabad, Telangana, India.\n"
            "Answer the user's questions truthfully and contextually based ONLY on the provided local knowledge context.\n"
            "If the context does not contain the answer, say that you do not have that specific information and offer to direct them to general public offices.\n"
            "Format your responses cleanly in Markdown. Cite the sources/documents provided in the context when mentioning facts.\n"
            "Keep answers engaging, helpful, and support multiple languages (English, Telugu, Hindi)."
        )

        formatted_history = ""
        if conversation_history:
            formatted_history = "\n--- Recent Conversation History ---\n"
            for msg in conversation_history[-6:]:  # Last 6 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                formatted_history += f"{role}: {msg['content']}\n"

        prompt = (
            f"{system_prompt}\n\n"
            f"--- Context (Local Knowledge) ---\n"
            f"{context}\n"
            f"{formatted_history}\n"
            f"--- Current User Query ---\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

        if settings.GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Gemini API generation error: {e}. Falling back to mock engine.")
        
        # Mock RAG generator fallback
        return self._generate_mock_response(query, context)

    def _generate_mock_response(self, query: str, context: str) -> str:
        """Generates a contextual response locally by analyzing keywords in the search context."""
        if not context or context.strip() == "No relevant context found.":
            return (
                "Hello! I am **HYBO**, your Hyderabad Smart City Assistant. "
                "I couldn't find specific official information about your query in our local databases. "
                "For general inquiries, you can check the Telangana Government portal or contact the GHMC helpline at 21111111.\n\n"
                "*Note: I am running in local offline demo mode.*"
            )

        # Basic text processing to make the mock response feel grounded in retrieved context
        lines = context.split("\n")
        citations = []
        matching_snippets = []
        
        for line in lines:
            if line.startswith("- Chunk") or line.startswith("Source:"):
                citations.append(line)
            elif line.strip() and not line.startswith("Source:"):
                # Grab a few descriptive sentences that match key terms
                matching_snippets.append(line)

        # Synthesize a response
        response = (
            f"### HYBO Local Response (Offline Demo Mode)\n\n"
            f"Based on Hyderabad's official reference datasets, here is what I found:\n\n"
        )
        
        # Add the first few snippets
        for snippet in matching_snippets[:3]:
            response += f"* {snippet}\n"
            
        response += f"\n\n**Sources Consulted:**\n"
        seen_sources = set()
        for cit in citations:
            source_info = cit.replace("Source: ", "").strip()
            if source_info and source_info not in seen_sources:
                seen_sources.add(source_info)
                response += f"- {source_info}\n"

        if not seen_sources:
            response += "- Hyderabad Smart City Knowledge Base\n"

        response += "\n\n*Note: To enable live Gemini responses, please set the `GEMINI_API_KEY` environment variable.*"
        return response

rag_manager = RAGManager()
