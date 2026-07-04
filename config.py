import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Company Research Assistant")

    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

    # Direct Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Crawler settings
    MAX_PAGES_TO_CRAWL: int = 6
    REQUEST_TIMEOUT: int = 10

    USEFUL_PATH_KEYWORDS = [
        "about", "product", "service", "solution", "contact", "pricing", "company"
    ]

    IGNORE_PATH_KEYWORDS = [
        "login", "signup", "register", "cart", "privacy", "terms",
        "career", "blog", "cookie", "policy", "legal", "sign-in", "sign-up"
    ]


settings = Settings()