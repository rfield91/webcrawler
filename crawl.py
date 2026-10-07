from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

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