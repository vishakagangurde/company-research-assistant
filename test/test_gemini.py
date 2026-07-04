import sys
import json

from services.utils import is_url, normalize_url, clean_company_name, extract_name_from_url
from services.serper_service import find_official_website, gather_all_public_info
from services.crawler_service import crawl_website
from services.gemini_service import generate_ai_report


REQUIRED_KEYS = [
    "company_name",
    "website",
    "phone_number",
    "address",
    "products_services",
    "company_summary",
    "ai_generated_pain_points",
    "competitors",
]


def validate_report(report: dict):
    print("=" * 80)
    print("VALIDATING GEMINI REPORT JSON STRUCTURE")
    print("=" * 80)

    missing_keys = []

    for key in REQUIRED_KEYS:
        if key not in report:
            missing_keys.append(key)

    if missing_keys:
        print("FAILED: Missing keys:")
        for key in missing_keys:
            print(f"- {key}")
        return False

    if not isinstance(report.get("products_services"), list):
        print("FAILED: products_services should be a list.")
        return False

    if not isinstance(report.get("ai_generated_pain_points"), list):
        print("FAILED: ai_generated_pain_points should be a list.")
        return False

    if not isinstance(report.get("competitors"), list):
        print("FAILED: competitors should be a list.")
        return False

    print("RESULT: Gemini report JSON structure is valid.")
    return True


def test_gemini(company_input: str):
    print("=" * 80)
    print("GEMINI AI REPORT TEST STARTED")
    print("=" * 80)
    print(f"Input: {company_input}")
    print()

    cleaned_input = clean_company_name(company_input)

    print("=" * 80)
    print("1. INPUT DETECTION")
    print("=" * 80)

    if is_url(cleaned_input):
        website = normalize_url(cleaned_input)
        company_name = extract_name_from_url(website)
        print("Input Type: Website URL")
        print(f"Company Name Extracted: {company_name}")
        print(f"Website: {website}")
    else:
        company_name = cleaned_input
        print("Input Type: Company Name")
        print(f"Company Name: {company_name}")

        print()
        print("=" * 80)
        print("2. FINDING OFFICIAL WEBSITE USING SERPER")
        print("=" * 80)

        website = find_official_website(company_name)
        print(f"Official Website Found: {website}")

        if not website:
            print("FAILED: Could not find official website.")
            return

    print()
    print("=" * 80)
    print("3. CRAWLING WEBSITE")
    print("=" * 80)

    crawled_pages = crawl_website(website)

    print(f"Total Pages Crawled: {len(crawled_pages)}")

    if not crawled_pages:
        print("FAILED: No pages crawled.")
        return

    print()
    print("=" * 80)
    print("4. COLLECTING PUBLIC INFO USING SERPER")
    print("=" * 80)

    public_info = gather_all_public_info(company_name)

    print(f"Overview Results: {len(public_info.get('overview', []))}")
    print(f"Products Results: {len(public_info.get('products', []))}")
    print(f"Headquarters Results: {len(public_info.get('headquarters', []))}")
    print(f"Pain Point Results: {len(public_info.get('pain_points', []))}")
    print(f"Competitor Results: {len(public_info.get('competitors', []))}")

    print()
    print("=" * 80)
    print("5. GENERATING AI REPORT USING DIRECT GEMINI API")
    print("=" * 80)

    report = generate_ai_report(
        company_name=company_name,
        website=website,
        crawled_pages=crawled_pages,
        public_info=public_info,
    )

    print("GEMINI REPORT GENERATED")
    print()

    print("=" * 80)
    print("GEMINI REPORT OUTPUT")
    print("=" * 80)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    is_valid = validate_report(report)

    output_file = "gemini_test_output.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 80)
    print("GEMINI TEST COMPLETED")
    print("=" * 80)
    print(f"Output saved to: {output_file}")

    summary = report.get("company_summary", "")

    if is_valid and summary and "Report generation failed" not in summary:
        print("RESULT: Direct Gemini API report generation is working properly.")
        print("NEXT STEP: Test PDF generation.")
    elif "Report generation failed" in summary:
        print("RESULT: Gemini returned fallback report.")
        print("Check GEMINI_API_KEY, model name, quota, or API access.")
    else:
        print("RESULT: Gemini partially worked, but report quality/structure needs checking.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python test_gemini.py Figma")
        print("python test_gemini.py https://www.figma.com")
        sys.exit(1)

    company_input = " ".join(sys.argv[1:])
    test_gemini(company_input)