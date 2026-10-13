import asyncio
import sys
from crawl import crawl_site_async
from json_report import write_json_report


async def main():
    if len(sys.argv) < 4:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = sys.argv[1]

    if not sys.argv[2].isdigit():
        print("max_concurrency must be an integer")
        sys.exit(1)
    if not sys.argv[3].isdigit():
        print("max_pages must be an integer")
        sys.exit(1)

    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    print(f"starting crawl of: {base_url}")

    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)

    print(f"Crawled {len(page_data)} pages")

    # for page, data in page_data.items():
    #     print(f"Url: {page}")
    #     print(f"\theading: {data["heading"]}")
    #     print(f"\tlinks: {len(data["outgoing_links"])}")
    #     print(f"\timages: {len(data["image_urls"])}")

    write_json_report(page_data)    

    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
