# api/index.py
# Vercel Python runtime entrypoint.
# Imports the FastAPI app from main.py and exposes it as `app`.

import sys
import os

# Make the project root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: F401 — Vercel looks for `app` in this file
