"""
FormGuide Field Detection & Schema Generator Engine
Analyzes static or interactive court PDFs to auto-extract AcroForm fields, text boundaries, and drawn underlines.
Outputs jurisdiction-agnostic, human-editable JSON form schemas.
"""

import argparse
import json
import os
import fitz  # PyMuPDF

def detect_pdf_fields(pdf_path, title="Detected Court Form"):
    doc = fitz.open(pdf_path)
    schema = {
        "title": title,
        "jurisdiction": "U.S. District Court / State Circuit Court",
        "template": os.path.relpath(pdf_path),
        "pages": len(doc),
        "fields": []
    }

    field_idx = 1
    seen_field_ids = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_height = page.rect.height
        
        # 1. Extract Native AcroForm Widgets
        widgets = list(page.widgets())
        for w in widgets:
            fid = w.field_name or f"widget_{field_idx}"
            if fid in seen_field_ids:
                fid = f"{fid}_{field_idx}"
            seen_field_ids.add(fid)

            rect = w.rect
            # Convert PyMuPDF rect to ReportLab point coordinates (Y origin at bottom-left)
            x0 = round(rect.x0, 1)
            y0 = round(page_height - rect.y1, 1)
            w_width = round(rect.width, 1)
            w_height = round(rect.height, 1)

            ftype = "text"
            if w.field_type_string in ["CheckBox", "RadioButton"]:
                ftype = "choice"
            elif w.field_type_string == "ComboBox":
                ftype = "select"

            schema["fields"].append({
                "id": fid,
                "prompt": f"Page {page_num+1} ({fid}):",
                "type": ftype,
                "page": page_num + 1,
                "x": x0,
                "y": y0,
                "width": w_width,
                "height": w_height,
                "font_size": 9 if w_height < 14 else 10,
                "acro_name": w.field_name
            })
            field_idx += 1

        # 2. Extract Vector Underlines if no native AcroForm widgets on page
        if not widgets:
            drawings = page.get_drawings()
            for draw in drawings:
                for item in draw.get("items", []):
                    if item[0] == "l":  # Line
                        p1, p2 = item[1], item[2]
                        if abs(p1.y - p2.y) < 3 and abs(p1.x - p2.x) > 30:
                            fid = f"underline_{field_idx}"
                            schema["fields"].append({
                                "id": fid,
                                "prompt": f"Page {page_num+1} Underline {field_idx}:",
                                "type": "text",
                                "page": page_num + 1,
                                "x": round(p1.x, 1),
                                "y": round(page_height - p1.y + 2, 1),
                                "width": round(abs(p1.x - p2.x), 1),
                                "font_size": 10
                            })
                            field_idx += 1

    return schema

def main():
    parser = argparse.ArgumentParser(description="FormGuide Automated Field Detector")
    parser.add_argument("--input", required=True, help="Path to input court PDF")
    parser.add_argument("--output", required=True, help="Path to output JSON schema")
    parser.add_argument("--title", default="Court Form Schema", help="Form Title")
    args = parser.parse_args()

    schema = detect_pdf_fields(args.input, args.title)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"✅ [FormGuide] Detected {len(schema['fields'])} form fields across {schema['pages']} pages.")
    print(f"📄 Saved Schema: {args.output}")

if __name__ == "__main__":
    main()
