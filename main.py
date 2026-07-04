import io
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from schemas import ResearchRequest, ResearchResponse
from services.utils import is_url, normalize_url, clean_company_name, extract_name_from_url, safe_filename
from services.serper_service import find_official_website, gather_all_public_info
from services.crawler_service import crawl_website
from services.gemini_service import generate_ai_report
from services.pdf_service import generate_pdf
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory store for generated PDFs (keyed by filename)
_pdf_cache: dict[str, bytes] = {}


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"app_name": settings.APP_NAME}
    )


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}


@app.post("/api/research", response_model=ResearchResponse)
def research_company(payload: ResearchRequest):
    try:
        user_input = clean_company_name(payload.company_input)

        if is_url(user_input):
            website = normalize_url(user_input)
            company_name = extract_name_from_url(website)
        else:
            company_name = user_input
            website = find_official_website(company_name, payload.serper_api_key)
            if not website:
                website = ""

        crawled_pages = crawl_website(website) if website else []

        public_info = gather_all_public_info(company_name, payload.serper_api_key)

        report = generate_ai_report(
            company_name=company_name,
            website=website,
            crawled_pages=crawled_pages,
            public_info=public_info,
            api_key=payload.gemini_api_key,
            model=payload.gemini_model,
        )

        pdf_bytes, pdf_filename = generate_pdf(report)

        # Cache the PDF bytes in memory for the download endpoint
        _pdf_cache[pdf_filename] = pdf_bytes

        return ResearchResponse(status="success", report=report, pdf_file=pdf_filename)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.get("/api/download-pdf/{file_name}")
def download_pdf(file_name: str):
    pdf_bytes = _pdf_cache.get(file_name)
    if not pdf_bytes:
        return JSONResponse(status_code=404, content={"status": "error", "message": "File not found or expired. Please regenerate the report."})
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)