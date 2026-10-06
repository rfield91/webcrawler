from urllib.parse import urlsplit
from bs4 import BeautifulSoup, Tag

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
