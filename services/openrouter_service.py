import json
import requests
from config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

REPORT_SCHEMA_EXAMPLE = {
    "company_name": "",
    "website": "",
    "phone_number": "",
    "address": "",
    "products_services": [],
    "company_summary": "",
    "ai_generated_pain_points": [],
    "competitors": [{"name": "", "website": ""}],
}


def _build_prompt(company_name: str, website: str, crawled_pages: list,
                   public_info: dict) -> str:
    crawled_text = "\n\n".join(
        f"URL: {p['url']}\nTITLE: {p['title']}\nCONTENT: {p['content']}"
        for p in crawled_pages
    )

    def _format_search(label, results):
        lines = [f"{label}:"]
        for r in results[:5]:
            lines.append(f"- {r.get('title','')}: {r.get('snippet','')} ({r.get('link','')})")
        return "\n".join(lines)

    search_text = "\n\n".join([
        _format_search("Company overview search results", public_info.get("overview", [])),
        _format_search("Products/services search results", public_info.get("products", [])),
        _format_search("Headquarters/contact search results", public_info.get("headquarters", [])),
        _format_search("Pain points search results", public_info.get("pain_points", [])),
        _format_search("Competitor search results", public_info.get("competitors", [])),
    ])

    prompt = f"""
You are a company research analyst. Using the data below, produce a structured
research report about "{company_name}" (website: {website}).

=== WEBSITE CRAWL DATA ===
{crawled_text}

=== PUBLIC SEARCH DATA ===
{search_text}

=== INSTRUCTIONS ===
Return ONLY valid JSON matching exactly this structure (no markdown, no commentary,
no text outside the JSON object):

{json.dumps(REPORT_SCHEMA_EXAMPLE, indent=2)}

Rules:
- "phone_number" and "address" should be "Not available" if unknown.
- "products_services" should be a list of short strings.
- "company_summary" should be 3-5 sentences.
- "ai_generated_pain_points" should be 3-5 plausible business pain points inferred
  from the data, phrased as short strings.
- "competitors" should list up to 5 competitors with name and website if known.
- Do not wrap the JSON in backticks. Return raw JSON only.
"""
    return prompt.strip()


def generate_ai_report(company_name: str, website: str, crawled_pages: list,
                        public_info: dict, api_key: str = None,
                        model: str = None) -> dict:
    """Sends gathered data to OpenRouter and parses the structured JSON report."""
    key = api_key or settings.OPENROUTER_API_KEY
    model_name = model or settings.OPENROUTER_MODEL

    if not key:
        return _fallback_report(company_name, website, "Missing OPENROUTER_API_KEY")

    prompt = _build_prompt(company_name, website, crawled_pages, public_info)

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()
        report = json.loads(cleaned)
        return _ensure_report_shape(report, company_name, website)
    except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
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
    return report


def _fallback_report(company_name: str, website: str, error: str) -> dict:
    return {
        "company_name": company_name,
        "website": website,
        "phone_number": "Not available",
        "address": "Not available",
        "products_services": [],
        "company_summary": f"Report generation failed: {error}",
        "ai_generated_pain_points": [],
        "competitors": [],
    }