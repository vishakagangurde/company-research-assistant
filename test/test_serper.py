import sys
import json
from services.serper_service import (
    find_official_website,
    search_company_overview,
    search_company_products,
    search_company_headquarters,
    search_company_pain_points,
    search_competitors,
    gather_all_public_info,
)


def print_results(title: str, results):
    print("=" * 80)
    print(title)
    print("=" * 80)

    if not results:
        print("No results found.")
        print()
        return

    for index, item in enumerate(results, start=1):
        print(f"RESULT {index}")
        print(f"Title   : {item.get('title', 'N/A')}")
        print(f"Link    : {item.get('link', 'N/A')}")
        print(f"Snippet : {item.get('snippet', 'N/A')}")
        print("-" * 80)

    print()


def test_serper(company_name: str):
    print("=" * 80)
    print("SERPER INTEGRATION TEST STARTED")
    print("=" * 80)
    print(f"Company Name: {company_name}")
    print()

    print("=" * 80)
    print("1. TESTING OFFICIAL WEBSITE SEARCH")
    print("=" * 80)

    official_website = find_official_website(company_name)

    print(f"Official Website Found: {official_website}")
    print()

    if not official_website:
        print("FAILED: Official website not found.")
        print("Possible reasons:")
        print("1. Missing or invalid SERPER_API_KEY")
        print("2. Serper API limit exhausted")
        print("3. Network issue")
        print("4. Search result parsing failed")
        return

    print("RESULT: Official website search is working.")
    print()

    overview = search_company_overview(company_name)
    products = search_company_products(company_name)
    headquarters = search_company_headquarters(company_name)
    pain_points = search_company_pain_points(company_name)
    competitors = search_competitors(company_name)

    print_results("2. COMPANY OVERVIEW RESULTS", overview)
    print_results("3. PRODUCTS / SERVICES RESULTS", products)
    print_results("4. HEADQUARTERS / CONTACT RESULTS", headquarters)
    print_results("5. PAIN POINT RESULTS", pain_points)
    print_results("6. COMPETITOR RESULTS", competitors)

    all_info = gather_all_public_info(company_name)

    output_file = "serper_test_output.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "company_name": company_name,
                "official_website": official_website,
                "public_info": all_info,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 80)
    print("SERPER TEST COMPLETED")
    print("=" * 80)
    print(f"Output saved to: {output_file}")

    if official_website and competitors:
        print("RESULT: Serper integration is working properly.")
    elif official_website:
        print("RESULT: Serper is partially working. Official website found, but competitor data may be weak.")
    else:
        print("RESULT: Serper integration failed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python test_serper.py Figma")
        sys.exit(1)

    company = " ".join(sys.argv[1:])
    test_serper(company)