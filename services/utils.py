import re
from urllib.parse import urlparse


def is_url(value: str) -> bool:
    """Detects whether the input string is a URL or a plain company name."""
    if not value:
        return False
    value = value.strip().lower()
    return value.startswith("http://") or value.startswith("https://") or value.startswith("www.")


def normalize_url(value: str) -> str:
    """Ensures the URL has a scheme."""
    value = value.strip()
    if value.lower().startswith("www."):
        value = "https://" + value
    if not value.lower().startswith("http"):
        value = "https://" + value
    return value


def clean_company_name(value: str) -> str:
    """Trims and normalizes a company name string."""
    return re.sub(r"\s+", " ", value.strip())


def extract_name_from_url(url: str) -> str:
    """Extracts a human-readable company name from a domain.

    https://www.figma.com -> Figma
    """
    parsed = urlparse(url if "://" in url else f"https://{url}")
    domain = parsed.netloc or parsed.path
    domain = domain.replace("www.", "")
    name = domain.split(".")[0]
    return name.capitalize()


def safe_filename(value: str) -> str:
    """Converts a company name into a safe filename."""
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower())
    return value.strip("_") or "company"