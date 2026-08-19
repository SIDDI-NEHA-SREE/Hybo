import socket
import ipaddress
from urllib.parse import urlparse, urljoin
import re
from typing import List, Dict, Any, Set
import httpx
from bs4 import BeautifulSoup
from app.utils.logger import logger

class WebScraper:
    @staticmethod
    def is_safe_url(url: str) -> bool:
        """
        Protects against SSRF by validating the protocol and resolving the hostname 
        to ensure it is not a private, loopback, or multicast IP address.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                logger.warning(f"URL {url} blocked: invalid scheme {parsed.scheme}")
                return False
                
            hostname = parsed.hostname
            if not hostname:
                logger.warning(f"URL {url} blocked: no hostname found")
                return False
                
            # Handle localhost explicitly
            if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
                logger.warning(f"URL {url} blocked: loopback hostname")
                return False

            # Resolve hostname to IP
            ip_str = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_str)
            
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast or ip_obj.is_unspecified:
                logger.warning(f"URL {url} resolved to unsafe IP {ip_str}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error checking safety of URL {url}: {str(e)}")
            return False

    @classmethod
    async def fetch_page(cls, url: str) -> str:
        """
        Fetches the raw HTML content of a URL using HTTPX with a strict timeout and size limit.
        """
        if not cls.is_safe_url(url):
            raise ValueError("URL points to an invalid protocol or private network address (SSRF Protection)")

        headers = {
            "User-Agent": "HYBO-Assistant-Web-Crawler/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # First send a HEAD request to check size limit
            try:
                head_resp = await client.head(url, headers=headers)
                content_length = int(head_resp.headers.get("content-length", 0))
                if content_length > 2 * 1024 * 1024:  # 2MB limit
                    raise ValueError("Target page size exceeds the 2MB limit")
            except httpx.HTTPError:
                pass  # Fall back to GET and check during stream

            # Fetch page content
            async with client.stream("GET", url, headers=headers) as response:
                if response.status_code != 200:
                    raise httpx.HTTPStatusError(
                        f"Non-200 status code received: {response.status_code}",
                        request=response.request,
                        response=response
                    )
                
                # Check Content-Type is text/html
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    raise ValueError(f"Unacceptable Content-Type: {content_type}. Only HTML pages can be scraped.")

                # Read body chunk by chunk up to 2MB
                chunks = []
                bytes_read = 0
                async for chunk in response.aiter_text():
                    bytes_read += len(chunk.encode("utf-8"))
                    if bytes_read > 2 * 1024 * 1024:
                        raise ValueError("Target page size exceeded 2MB limit during stream")
                    chunks.append(chunk)
                
                return "".join(chunks)

    @staticmethod
    def clean_html(html_content: str) -> Dict[str, str]:
        """
        Parses HTML, removes boilerplate (script, style, footers, headers, nav, sidebars),
        and extracts structured text content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Get page title
        title = "Untitled Page"
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Remove irrelevant elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript", "svg"]):
            tag.decompose()

        # Target content blocks: headings, paragraphs, lists, tables
        # Gather text elements in document order
        elements = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th"])
        
        cleaned_lines = []
        for el in elements:
            text = el.get_text().strip()
            if not text:
                continue
            
            # Add prefix for headers to keep structure hint
            if el.name.startswith("h") and len(text) < 150:
                cleaned_lines.append(f"\n{text}\n")
            elif el.name == "li":
                cleaned_lines.append(f"- {text}")
            else:
                cleaned_lines.append(text)

        # Merge text with spacing
        full_text = "\n".join(cleaned_lines)
        
        # Clean extra white space/newlines
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)
        full_text = re.sub(r" {2,}", " ", full_text)
        
        return {
            "title": title,
            "text": full_text.strip()
        }

    @classmethod
    async def crawl_and_extract(cls, base_url: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Scrapes the main URL and crawls internal links of the same domain up to max_pages total.
        Protects against infinite loops, invalid urls, and SSRF.
        """
        results: List[Dict[str, Any]] = []
        visited_urls: Set[str] = set()
        to_visit: List[str] = [base_url]
        
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc.lower()

        logger.info(f"Initiating RAG scrape/crawl for {base_url} (max {max_pages} pages)")

        while to_visit and len(results) < max_pages:
            current_url = to_visit.pop(0)
            
            # Normalize url (strip fragments/query parameters)
            parsed_current = urlparse(current_url)
            normalized_url = parsed_current._replace(fragment="", query="").geturl()

            if normalized_url in visited_urls:
                continue
            visited_urls.add(normalized_url)

            try:
                html = await cls.fetch_page(normalized_url)
                extracted = cls.clean_html(html)
                
                results.append({
                    "url": normalized_url,
                    "title": extracted["title"],
                    "text": extracted["text"]
                })
                
                # If we haven't reached page limit, extract links on this page to crawl next
                if len(results) < max_pages:
                    soup = BeautifulSoup(html, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"].strip()
                        full_href = urljoin(normalized_url, href)
                        parsed_href = urlparse(full_href)
                        
                        # Only crawl links on the same domain and using http/https
                        if parsed_href.netloc.lower() == base_domain and parsed_href.scheme in ("http", "https"):
                            clean_href = parsed_href._replace(fragment="", query="").geturl()
                            if clean_href not in visited_urls and clean_href not in to_visit:
                                to_visit.append(clean_href)
            except Exception as e:
                logger.warning(f"Failed to scrape URL '{normalized_url}': {str(e)}")
                # If it is the base URL that failed, raise it so the user receives a direct error
                if normalized_url == base_url:
                    raise Exception(f"Failed to access main webpage: {str(e)}")

        return results

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """
        Splits text into chunks of character size with sliding overlap window.
        """
        chunks = []
        if not text:
            return chunks

        # Basic sliding character chunking
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += (chunk_size - overlap)
            
        return chunks
