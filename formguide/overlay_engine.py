"""
FormGuide Overlay Engine
Merges structured JSON answers directly onto static PDF court forms at precise point coordinates using ReportLab and PyPDF.
"""

import os
import io
import json
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_overlay_pdf(schema_data, answers):
    """
    Generates a multi-page overlay PDF containing vector text positioned at exact schema coordinates.
    """
    total_pages = schema_data.get("pages", 1)
    packet_buffer = io.BytesIO()
    c = canvas.Canvas(packet_buffer, pagesize=letter)

    # Group fields by page
    fields_by_page = {}
    for field in schema_data.get("fields", []):
        p = field.get("page", 1)
        fields_by_page.setdefault(p, []).append(field)

    for page_num in range(1, total_pages + 1):
        page_fields = fields_by_page.get(page_num, [])
        for field in page_fields:
            field_id = field.get("id")
            val = answers.get(field_id, "")
            if not val:
                continue

            x = field.get("x", 100)
            y = field.get("y", 100)
            font_size = field.get("font_size", 10)
            font_name = field.get("font", "Helvetica")

            c.setFont(font_name, font_size)
            c.drawString(x, y, str(val))

        c.showPage()

    c.save()
    packet_buffer.seek(0)
    return packet_buffer.getvalue()

def apply_overlay_to_template(template_pdf_path, overlay_pdf_bytes, output_pdf_path):
    """
    Merges the generated overlay PDF bytes onto the static template PDF.
    """
    template_reader = PdfReader(template_pdf_path)
    overlay_reader = PdfReader(io.BytesIO(overlay_pdf_bytes))
    writer = PdfWriter()

    for idx, template_page in enumerate(template_reader.pages):
        if idx < len(overlay_reader.pages):
            overlay_page = overlay_reader.pages[idx]
            template_page.merge_page(overlay_page)
        writer.add_page(template_page)

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"[+] FormGuide: E-Filing Ready PDF generated successfully at {output_pdf_path}")
    return True

def fill_form_from_answers(schema_path, answers_dict, output_pdf_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_data = json.load(f)

    template_path = schema_data.get("template")
    if not os.path.isabs(template_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, template_path)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template PDF not found: {template_path}")

    overlay_bytes = generate_overlay_pdf(schema_data, answers_dict)
    return apply_overlay_to_template(template_path, overlay_bytes, output_pdf_path)
