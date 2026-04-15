from __future__ import annotations

import io
import json

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def export_analysis_json(record: dict) -> bytes:
    return json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")


def export_analysis_excel(record: dict) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Analysis"

    rows = [
        ("ID", record["id"]),
        ("Query", record["query"]),
        ("Model", record["model"]),
        ("Location", record["location_name"]),
        ("Latitude", record["latitude"]),
        ("Longitude", record["longitude"]),
        ("Coordinate System", record["coordinate_system"]),
        ("Created At", record["created_at"]),
        ("Analysis", record["response"].get("analysis", "")),
        ("Confidence", record["response"].get("confidence", "")),
        ("Tags", ", ".join(record["response"].get("enriched_tags", []))),
        ("Recommendations", json.dumps(record["response"].get("recommendations", []), ensure_ascii=False)),
    ]
    for key, value in rows:
        sheet.append([key, value])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def export_analysis_pdf(record: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"GEO Analysis #{record['id']}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Query: {record['query']}", styles["BodyText"]),
        Paragraph(f"Model: {record['model']}", styles["BodyText"]),
        Paragraph(f"Location: {record['location_name'] or 'N/A'}", styles["BodyText"]),
        Paragraph(f"Created At: {record['created_at']}", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Analysis", styles["Heading2"]),
        Paragraph(record["response"].get("analysis", ""), styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Tags", styles["Heading2"]),
        Paragraph(", ".join(record["response"].get("enriched_tags", [])) or "N/A", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Recommendations", styles["Heading2"]),
    ]

    for item in record["response"].get("recommendations", []):
        story.append(Paragraph(f"{item.get('title', '')}: {item.get('reason', '')}", styles["BodyText"]))
        story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()
