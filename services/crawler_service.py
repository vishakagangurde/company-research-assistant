import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from config import settings


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CompanyResearchBot/1.0; +https://example.com/bot)"
}


DEFAULT_PATHS = [
    "/",
    "/about",
    "/about-us",
    "/company",
    "/products",
    "/product",
    "/services",
    "/solutions",
    "/pricing",
    "/contact",
    "/contact-us",
]


def _normalize_crawl_url(url: str) -> str:
    """
    Normalizes URL for consistent crawling and duplicate prevention.
    """
    if not url:
        return ""

    url = url.strip()

    if url.startswith("www."):
        url = "https://" + url

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urlparse(url)

    # Remove fragments and query params for cleaner deduplication
    cleaned = parsed._replace(query="", fragment="")

    final_url = urlunparse(cleaned)

    # Keep root URL clean, but remove trailing slash for non-root paths
    if final_url.endswith("/") and parsed.path not in ["", "/"]:
        final_url = final_url.rstrip("/")

    return final_url


def _get(url: str):
    """
    Fetches a web page safely.
    """
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=settings.REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type:
            return None

        return response

    except requests.RequestException:
        return None


def _clean_text(text: str) -> str:
    """
    Cleans extra spaces and repeated whitespace.
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_text(html: str) -> str:
    """
    Extracts useful visible text from HTML.
    Removes noisy tags like nav, footer, script, style, etc.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove noisy/non-content tags
    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "form",
        "input",
        "button",
        "nav",
        "header",
        "footer",
        "aside",
    ]):
        tag.decompose()

    # Prefer main content if available
    main_content = soup.find("main")
    if main_content:
        text = main_content.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)

    text = _clean_text(text)

    # Keep prompt size controlled
    return text[:3000]


def _get_title(html: str) -> str:
    """
    Extracts page title.
    """
    soup = BeautifulSoup(html, "html.parser")

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return ""


def _is_same_domain(base_url: str, candidate_url: str) -> bool:
    """
    Checks whether the candidate URL belongs to the same domain.
    """
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    candidate_domain = urlparse(candidate_url).netloc.replace("www.", "")

    return base_domain == candidate_domain


def _is_useful_link(url: str) -> bool:
    """
    Decides whether a link is useful for company research.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()

    if not path or path == "/":
        return True

    if any(bad in path for bad in settings.IGNORE_PATH_KEYWORDS):
        return False

    if any(good in path for good in settings.USEFUL_PATH_KEYWORDS):
        return True

    return False


def _score_link(url: str) -> int:
    """
    Gives priority to important company pages.
    Lower score means higher priority.
    """
    path = urlparse(url).path.lower()

    if path in ["/", ""]:
        return 0
    if "about" in path:
        return 1
    if "product" in path:
        return 2
    if "service" in path:
        return 3
    if "solution" in path:
        return 4
    if "pricing" in path:
        return 5
    if "contact" in path:
        return 6
    if "company" in path:
        return 7

    return 20


def _discover_internal_links(base_url: str, html: str) -> list:
    """
    Finds useful internal links from the homepage.
    """
    soup = BeautifulSoup(html, "html.parser")
    discovered_links = []

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()

        if not href:
            continue

        if href.startswith("mailto:") or href.startswith("tel:"):
            continue

        full_url = urljoin(base_url, href)
        full_url = _normalize_crawl_url(full_url)

        if not _is_same_domain(base_url, full_url):
            continue

        if not _is_useful_link(full_url):
            continue

        discovered_links.append(full_url)

    # Add fallback useful paths manually
    for path in DEFAULT_PATHS:
        fallback_url = urljoin(base_url, path)
        fallback_url = _normalize_crawl_url(fallback_url)
        discovered_links.append(fallback_url)

    # Deduplicate
    unique_links = []
    seen = set()

    for link in discovered_links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    # Sort important pages first
    unique_links.sort(key=_score_link)

    return unique_links


def crawl_website(base_url: str) -> list:
    """
    Crawls homepage and selected useful internal pages.

    Returns:
    [
        {
            "url": "...",
            "title": "...",
            "content": "..."
        }
    ]
    """
    results = []
    visited = set()

    if not base_url:
        return results

    base_url = _normalize_crawl_url(base_url)

    homepage_response = _get(base_url)

    if homepage_response is None:
        return results

    homepage_html = homepage_response.text

    homepage_content = _extract_text(homepage_html)
    homepage_title = _get_title(homepage_html)

    if homepage_content:
        results.append({
            "url": base_url,
            "title": homepage_title,
            "content": homepage_content,
        })

    visited.add(base_url)

    candidate_links = _discover_internal_links(base_url, homepage_html)

    for link in candidate_links:
        if len(results) >= settings.MAX_PAGES_TO_CRAWL:
            break

        link = _normalize_crawl_url(link)

        if link in visited:
            continue

        visited.add(link)

        response = _get(link)

        if response is None:
            continue

        html = response.text
        title = _get_title(html)
        content = _extract_text(html)

        if not content or len(content) < 100:
            continue

        results.append({
            "url": link,
            "title": title,
            "content": content,
        })

    return results