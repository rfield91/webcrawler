import asyncio
import sys
from crawl import crawl_site_async


async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = sys.argv[1]

    print(f"starting crawl of: {base_url}")

    page_data = await crawl_site_async(base_url)

    print(f"Crawled {len(page_data)} pages")

    for page, data in page_data.items():
        print(f"Url: {page}")
        print(f"\theading: {data["heading"]}")
        print(f"\tlinks: {len(data["outgoing_links"])}")
        print(f"\timages: {len(data["image_urls"])}")

if __name__ == "__main__":
    asyncio.run(main())
