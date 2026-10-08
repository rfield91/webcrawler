import asyncio
from types import TracebackType
import aiohttp
from operator import contains
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import requests

def normalize_url(url) -> str:
    parsed_url = urlsplit(url)
    full_path = f"{parsed_url.netloc}{parsed_url.path}"
    full_path = full_path.rstrip("/")

    if not full_path.startswith("www."):
        full_path = f"www.{full_path}"

    return full_path.lower()

def get_heading_from_html(html) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")

    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""
    
def get_first_paragraph_from_html(html) -> str:
    soup = BeautifulSoup(html, "html.parser")

    main_tag = soup.find("main")

    p_tag = None

    if isinstance(main_tag, Tag):
        p_tag = main_tag.find("p")
    if not isinstance(p_tag, Tag):
        p_tag = soup.find("p")

    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    html_links = soup.find_all("a")

    links = []

    for html_link in html_links:
        url = html_link.get("href")

        if url is None:
            continue
        
        links.append(urljoin(base_url, url))

    return links

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    html_images = soup.find_all("img")

    links = []

    for html_image in html_images:
        url = html_image.get("src")

        if url is None:
            continue
        
        links.append(urljoin(base_url, url))

    return links

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url)
    }

class AsyncCrawler:

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.visited: set[str] = set[str]()
        self.lock = asyncio.Lock()
        self.max_concurrency = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(
            self, 
            exc_type: type[BaseException] | None, 
            exc_val: BaseException | None, 
            exc_tb: TracebackType | None
        ):
        if self.session is not None:
            await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if normalized_url in self.visited:
                return False
            
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url):
        if self.session is None:
            return None

        try:
            async with self.session.get(
                url,
                headers={
                    "User-Agent": "BootCrawler/1.0"
                }
            ) as response:
                if response.status >= 400:
                    raise Exception(f"Failed to get {url}, status code: {response.status_code}")

                content_type = response.headers.get("content-type")

                if "text/html" not in content_type:
                    raise Exception(f"Invalid content type getting {url}, content-type is: {content_type}")

                return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def crawl_page(self, current_url=None):
        parsed_current_url = urlsplit(current_url)

        if self.base_domain != parsed_current_url.netloc:
            return

        normalized_current_url = normalize_url(current_url)

        if not await self.add_page_visit(normalized_current_url):
            return
        
        async with self.semaphore:
            print(f"Getting html for: {current_url}")
            html = await self.get_html(current_url)

            if html is None:
                return

            current_page_data = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_current_url] = current_page_data

        tasks: list[asyncio.Task[None]] = []

        for url in current_page_data["outgoing_links"]:
            tasks.append(asyncio.create_task(self.crawl_page(url)))

        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page(current_url=self.base_url)
        return self.page_data

async def crawl_site_async(base_url):
    async with AsyncCrawler(base_url) as asyncCrawler:
        return await asyncCrawler.crawl()