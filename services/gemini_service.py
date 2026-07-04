import json
import re
import requests
from config import settings


REPORT_SCHEMA_EXAMPLE = {
    "company_name": "",
    "website": "",
    "phone_number": "",
    "address": "",
    "products_services": [],
    "company_summary": "",
    "ai_generated_pain_points": [],
    "competitors": [
        {
            "name": "",
            "website": ""
        }
    ]
}


def _build_prompt(company_name: str, website: str, crawled_pages: list, public_info: dict) -> str:
    crawled_text = "\n\n".join(
        f"URL: {p.get('url', '')}\nTITLE: {p.get('title', '')}\nCONTENT: {p.get('content', '')}"
        for p in crawled_pages
    )

    def format_search(label: str, results: list) -> str:
        lines = [f"{label}:"]
        for r in results[:5]:
            lines.append(
                f"- {r.get('title', '')}: {r.get('snippet', '')} ({r.get('link', '')})"
            )
        return "\n".join(lines)

    search_text = "\n\n".join([
        format_search("Company overview search results", public_info.get("overview", [])),
        format_search("Products/services search results", public_info.get("products", [])),
        format_search("Headquarters/contact search results", public_info.get("headquarters", [])),
        format_search("Pain points search results", public_info.get("pain_points", [])),
        format_search("Competitor search results", public_info.get("competitors", [])),
    ])

    prompt = f"""
You are a company research analyst.

Generate a structured company research report for the company below.

Company Name: {company_name}
Website: {website}

Use the website crawl data and public search data.

WEBSITE CRAWL DATA:
{crawled_text}

PUBLIC SEARCH DATA:
{search_text}

Return ONLY valid JSON.
Do not use markdown.
Do not add explanation outside JSON.
Do not wrap JSON inside backticks.

The JSON must match exactly this structure:

{json.dumps(REPORT_SCHEMA_EXAMPLE, indent=2)}

Rules:
- company_name should be the actual company name.
- website should be the official website.
- phone_number should be "Not available" if unknown.
- address should be "Not available" if unknown.
- products_services must be a list of short strings.
- company_summary must be 3 to 5 sentences.
- Pain points should be neutral, business-focused, and non-accusatory. Avoid legal claims such as fraud, deceptive marketing, or accusations unless explicitly supported by trusted sources.
- For competitors, always provide the official website if it is commonly known. If unsure, use "Not available". Do not leave all competitor websites as "Not available" when competitors are globally known companies.
- Each competitor must have name and website.
"""
    return prompt.strip()


def _extract_json(text: str) -> dict:
    """
    Extracts JSON from Gemini response.
    Handles raw JSON, markdown-wrapped JSON, and extra text.
    """
    if not text:
        raise ValueError("Empty Gemini response")

    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response")

    return json.loads(match.group(0))


def generate_ai_report(
    company_name: str,
    website: str,
    crawled_pages: list,
    public_info: dict,
    api_key: str = None,
    model: str = None,
) -> dict:
    """
    Generates company research report using direct Google Gemini API.
    """
    key = api_key or settings.GEMINI_API_KEY
    model_name = model or settings.GEMINI_MODEL

    if not key:
        return _fallback_report(company_name, website, "Missing GEMINI_API_KEY")

    prompt = _build_prompt(
        company_name=company_name,
        website=website,
        crawled_pages=crawled_pages,
        public_info=public_info,
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent?key={key}"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return _fallback_report(company_name, website, "No candidates returned from Gemini")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        if not parts:
            return _fallback_report(company_name, website, "No response parts returned from Gemini")

        raw_output = parts[0].get("text", "")

        report = _extract_json(raw_output)

        return _ensure_report_shape(report, company_name, website)

    except Exception as e:
        return _fallback_report(company_name, website, str(e))


def _ensure_report_shape(report: dict, company_name: str, website: str) -> dict:
    report.setdefault("company_name", company_name)
    report.setdefault("website", website)
    report.setdefault("phone_number", "Not available")
    report.setdefault("address", "Not available")
    report.setdefault("products_services", [])
    report.setdefault("company_summary", "")
    report.setdefault("ai_generated_pain_points", [])
    report.setdefault("competitors", [])

    if not isinstance(report["products_services"], list):
        report["products_services"] = []

    if not isinstance(report["ai_generated_pain_points"], list):
        report["ai_generated_pain_points"] = []

    if not isinstance(report["competitors"], list):
        report["competitors"] = []

    cleaned_competitors = []
    for competitor in report["competitors"]:
        if isinstance(competitor, dict):
            cleaned_competitors.append({
                "name": competitor.get("name", ""),
                "website": competitor.get("website", "")
            })
        elif isinstance(competitor, str):
            cleaned_competitors.append({
                "name": competitor,
                "website": ""
            })

    report["competitors"] = cleaned_competitors

    return report


def _fallback_report(company_name: str, website: str, error: str) -> dict:
    return {
        "company_name": company_name,
        "website": website,
        "phone_number": "Not available",
        "address": "Not available",
        "products_services": [],
        "company_summary": f"Report generation failed using Gemini API: {error}",
        "ai_generated_pain_points": [],
        "competitors": [],
    }