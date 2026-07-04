import sys
import json
from services.crawler_service import crawl_website


def test_crawler(url: str):
    print("=" * 80)
    print("WEB CRAWLER TEST STARTED")
    print("=" * 80)
    print(f"Target URL: {url}")
    print()

    pages = crawl_website(url)

    print("=" * 80)
    print("CRAWLER SUMMARY")
    print("=" * 80)
    print(f"Total pages crawled: {len(pages)}")
    print()

    if not pages:
        print("FAILED: No pages were crawled.")
        print()
        print("Possible reasons:")
        print("1. Website blocks crawlers")
        print("2. URL is incorrect")
        print("3. Internet issue")
        print("4. Request timeout")
        print("5. Website requires JavaScript rendering")
        return

    for index, page in enumerate(pages, start=1):
        url = page.get("url", "")
        title = page.get("title", "")
        content = page.get("content", "")

        print("-" * 80)
        print(f"PAGE {index}")
        print("-" * 80)
        print(f"URL: {url}")
        print(f"TITLE: {title}")
        print(f"CONTENT LENGTH: {len(content)} characters")
        print()
        print("CONTENT PREVIEW:")
        print(content[:500])
        print()

    output_file = "crawler_test_output.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print("CRAWLER TEST COMPLETED")
    print("=" * 80)
    print(f"Output saved to: {output_file}")

    if len(pages) >= 2:
        print("RESULT: Crawler is working properly.")
    elif len(pages) == 1:
        print("RESULT: Crawler is partially working. It crawled only homepage.")
        print("You may need to improve internal link discovery.")
    else:
        print("RESULT: Crawler failed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python test_crawler.py https://www.example.com")
        sys.exit(1)

    test_url = sys.argv[1]
    test_crawler(test_url)