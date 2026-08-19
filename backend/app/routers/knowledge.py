import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, BackgroundTasks, status, Query

from app.schemas import URLIngestRequest, URLSourceStatus, URLSourceListResponse
from app.services.web_scraper import WebScraper
from app.services.vector_store import VectorStore
from app.utils.logger import logger

router = APIRouter(prefix="/api/knowledge", tags=["Website Knowledge"])

async def ingest_url_worker(url: str):
    """
    Background worker that runs the crawling, HTML cleaning, and embedding pipeline.
    """
    try:
        logger.info(f"Background worker starting crawl for '{url}'")
        # Ingest a maximum of 5 pages for domain depth traversal
        pages = await WebScraper.crawl_and_extract(url, max_pages=5)
        
        if not pages:
            raise ValueError("No pages could be scraped or extracted from the URL.")

        logger.info(f"Crawl complete for '{url}': extracted {len(pages)} pages. Generating embeddings...")
        await VectorStore.add_chunks(url, pages)
        logger.info(f"Background ingestion worker finished successfully for '{url}'")
    except Exception as e:
        logger.error(f"Background ingestion task failed for '{url}': {str(e)}")
        VectorStore.update_source_status(
            url=url,
            status="failed",
            message=str(e),
            pages_count=0
        )

@router.post("/url", status_code=status.HTTP_202_ACCEPTED, response_model=URLSourceStatus)
async def ingest_url(request: URLIngestRequest, background_tasks: BackgroundTasks):
    """
    Spawns a background task to crawl and ingest a website.
    """
    url = request.url.strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL string cannot be empty"
        )
        
    # Safe validation checks
    if not WebScraper.is_safe_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL scheme or target address (SSRF Protection block)"
        )

    # Register as processing in vector store
    VectorStore.update_source_status(
        url=url,
        status="processing",
        message=None,
        pages_count=0
    )

    # Queue background processing task
    background_tasks.add_task(ingest_url_worker, url)

    return URLSourceStatus(
        url=url,
        status="processing",
        message=None,
        pages_count=0,
        updated_at=datetime.now(timezone.utc).isoformat()
    )

@router.get("/sources", response_model=URLSourceListResponse)
async def get_sources():
    """
    Retrieves all website sources that have been added.
    """
    try:
        sources_list = VectorStore.get_sources()
        statuses = []
        for s in sources_list:
            statuses.append(URLSourceStatus(
                url=s["url"],
                status=s["status"],
                message=s.get("message"),
                pages_count=s.get("pages_count", 0),
                updated_at=s.get("updated_at", datetime.now(timezone.utc).isoformat())
            ))
        return URLSourceListResponse(success=True, sources=statuses)
    except Exception as e:
        logger.error(f"Failed to query knowledge sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sources: {str(e)}"
        )

@router.delete("/url")
async def delete_url(url: str = Query(..., description="The website URL to delete")):
    """
    Removes a website source and deletes all associated embeddings.
    """
    url = url.strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required"
        )
        
    try:
        # Check if exists
        sources = VectorStore.get_sources()
        exists = any(s["url"] == url for s in sources)
        
        VectorStore.delete_source(url)
        
        if not exists:
            return {"success": True, "message": f"URL '{url}' was not found, but cleanup completed"}
            
        return {"success": True, "message": f"Successfully deleted source '{url}' and cleared its knowledge index"}
    except Exception as e:
        logger.error(f"Failed to delete source URL '{url}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete source URL: {str(e)}"
        )
