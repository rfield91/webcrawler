import asyncio
from types import TracebackType
import aiohttp
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

def _host(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")

def normalize_url(url) -> str:
    parsed = urlsplit(url)
    key = f"{_host(url)}{parsed.path.rstrip('/')}"

    return f"{key}?{parsed.query}" if parsed.query else key

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

    def __init__(self, base_url: str, max_concurrency: int, max_pages: int) -> None:
        self.base_url = base_url
        self.base_domain = _host(base_url)
        self.max_concurrency: int = max_concurrency
        self.max_pages: int = max_pages

        self.page_data: dict[str, PageData] = {}
        self.seen: set[str] = set()
        self.queue: asyncio.Qeuue[str] = asyncio.Queue()
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "BootCrawler/1.0"},
        )
        return self

    async def __aexit__(
            self, 
            exc_type: type[BaseException] | None, 
            exc_val: BaseException | None, 
            exc_tb: TracebackType | None
        ):
        if self.session is not None:
            await self.session.close()

    def enqueue(self, url: str) -> None:
        if _host(url) != self.base_domain:
            return

        key = normalize_url(url)
        
        if key in self.seen:
            return

        if len(self.seen) >= self.max_pages:
            return

        self.seen.add(key)
        self.queue.put_nowait(url)

    async def get_html(self, url):
        if self.session is None:
            return None

        try:
            async with self.session.get(url) as response:
                if response.status >= 400:
                    raise Exception(f"Failed to get {url}, status code: {response.status_code}")

                content_type = response.headers.get("content-type")

                if "text/html" not in content_type:
                    raise Exception(f"Invalid content type getting {url}, content-type is: {content_type}")

                return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def crawl_page(self, url=None):
        print(f"Getting html for: {url}")
        html = await self.get_html(url)

        if html is None:
            return

        data = extract_page_data(html, url)

        self.page_data[normalize_url(url)] = data

        for link in data["outgoing_links"]:
            self.enqueue(link)

    async def worker(self):
        while True:
            url = await self.queue.get()
            try:
                await self.crawl_page(url)
            except Exception:
                print(f"Unexecpted error crawling {url}")
            finally:
                self.queue.task_done()

    async def crawl(self):
        self.enqueue(self.base_url)

        workers = [asyncio.create_task(self.worker()) for _ in range(self.max_concurrency)]

        try:
            await self.queue.join()
        finally:
            for w in workers:
                w.cancel()
            
            await asyncio.gather(*workers, return_exceptions=True)

        return self.page_data

async def crawl_site_async(base_url: str, max_concurrency: int, max_pages: int):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as asyncCrawler:
        return await asyncCrawler.crawl()