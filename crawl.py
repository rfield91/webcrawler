from urllib.parse import urlsplit

def normalize_url(url):
    parsed_url = urlsplit(url)
    full_path = f"{parsed_url.netloc}{parsed_url.path}"
    full_path = full_path.rstrip("/")

    if not full_path.startswith("www."):
        full_path = f"www.{full_path}"

    return full_path.lower()