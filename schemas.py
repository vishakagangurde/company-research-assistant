from pydantic import BaseModel, Field
from typing import List, Optional


class ResearchRequest(BaseModel):
    company_input: str = Field(..., description="Company name or website URL")
    applicant_name: Optional[str] = ""
    applicant_email: Optional[str] = ""
    serper_api_key: Optional[str] = None

    # Direct Gemini API fields
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None


class Competitor(BaseModel):
    name: str = ""
    website: str = ""


class CompanyReport(BaseModel):
    company_name: str = ""
    website: str = ""
    phone_number: str = "Not available"
    address: str = "Not available"
    products_services: List[str] = []
    company_summary: str = ""
    ai_generated_pain_points: List[str] = []
    competitors: List[Competitor] = []


class ResearchResponse(BaseModel):
    status: str
    report: Optional[CompanyReport] = None
    pdf_file: Optional[str] = None
    message: Optional[str] = None
