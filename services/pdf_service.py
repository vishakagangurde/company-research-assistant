import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from config import settings
from services.utils import safe_filename


def generate_pdf(report: dict) -> str:
    """Builds a PDF research report and returns the filename (not full path)."""
    company_name = report.get("company_name", "company")
    filename = f"{safe_filename(company_name)}_research_report.pdf"
    filepath = os.path.join(settings.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                             topMargin=0.7 * inch, bottomMargin=0.7 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=20, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], spaceBefore=14, spaceAfter=8,
        textColor=colors.HexColor("#1f2937")
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["BodyText"], leading=16
    )

    story = []

    story.append(Paragraph("AI Company Research Report", title_style))

    # Company Information
    story.append(Paragraph("Company Information", heading_style))
    info_data = [
        ["Company Name", company_name],
        ["Website", report.get("website", "Not available")],
        ["Phone Number", report.get("phone_number", "Not available")],
        ["Address", report.get("address", "Not available")],
    ]
    info_table = Table(info_data, colWidths=[1.6 * inch, 4.4 * inch])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Products / Services
    story.append(Paragraph("Products / Services", heading_style))
    products = report.get("products_services", [])
    if products:
        for p in products:
            story.append(Paragraph(f"• {p}", body_style))
    else:
        story.append(Paragraph("Not available", body_style))
    story.append(Spacer(1, 8))

    # Company Summary
    story.append(Paragraph("Company Summary", heading_style))
    story.append(Paragraph(report.get("company_summary", "Not available"), body_style))
    story.append(Spacer(1, 8))

    # Pain Points
    story.append(Paragraph("AI-generated Pain Points", heading_style))
    pain_points = report.get("ai_generated_pain_points", [])
    if pain_points:
        for pp in pain_points:
            story.append(Paragraph(f"• {pp}", body_style))
    else:
        story.append(Paragraph("Not available", body_style))
    story.append(Spacer(1, 8))

    # Competitors
    story.append(Paragraph("Competitor Information", heading_style))
    competitors = report.get("competitors", [])
    if competitors:
        comp_data = [["Competitor Name", "Website"]]
        for c in competitors:
            comp_data.append([c.get("name", ""), c.get("website", "")])
        comp_table = Table(comp_data, colWidths=[2.5 * inch, 3.5 * inch])
        comp_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(comp_table)
    else:
        story.append(Paragraph("Not available", body_style))

    doc.build(story)
    return filename