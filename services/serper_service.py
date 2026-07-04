import requests
from config import settings

SERPER_URL = "https://google.serper.dev/search"


def _search(query: str, api_key: str, num: int = 5) -> dict:
    """Runs a single Serper.dev search query and returns the raw JSON result."""
    key = api_key or settings.SERPER_API_KEY
    if not key:
        return {"organic": [], "error": "Missing SERPER_API_KEY"}

    headers = {
        "X-API-KEY": key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": num}

    try:
        resp = requests.post(SERPER_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"organic": [], "error": str(e)}


def find_official_website(company_name: str, api_key: str = None) -> str:
    """Uses Serper to find the most likely official website for a company name."""
    data = _search(f"{company_name} official website", api_key, num=5)
    organic = data.get("organic", [])
    if organic:
        return organic[0].get("link", "")
    return ""


def search_company_overview(company_name: str, api_key: str = None) -> list:
    """Collects general public info about a company."""
    data = _search(f"{company_name} company overview", api_key, num=5)
    return data.get("organic", [])


def search_company_products(company_name: str, api_key: str = None) -> list:
    """Collects info about a company's products/services."""
    data = _search(f"{company_name} products and services", api_key, num=5)
    return data.get("organic", [])


def search_company_headquarters(company_name: str, api_key: str = None) -> list:
    """Collects info about a company's HQ / contact details."""
    data = _search(f"{company_name} company headquarters contact", api_key, num=5)
    return data.get("organic", [])


def search_company_pain_points(company_name: str, api_key: str = None) -> list:
    """Collects info hinting at business pain points."""
    data = _search(f"{company_name} business challenges pain points", api_key, num=5)
    return data.get("organic", [])


def search_competitors(company_name: str, api_key: str = None) -> list:
    """Finds competitors for a company."""
    data = _search(f"{company_name} competitors", api_key, num=5)
    return data.get("organic", [])


def gather_all_public_info(company_name: str, api_key: str = None) -> dict:
    """Runs all Serper searches needed for the report and bundles the results."""
    return {
        "overview": search_company_overview(company_name, api_key),
        "products": search_company_products(company_name, api_key),
        "headquarters": search_company_headquarters(company_name, api_key),
        "pain_points": search_company_pain_points(company_name, api_key),
        "competitors": search_competitors(company_name, api_key),
    }