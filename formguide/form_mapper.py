"""
FormGuide Field Detection Engine
Analyzes static PDFs to extract text boundaries, lines, and underlines.
"""

import argparse
import json
import fitz  # PyMuPDF

def detect_pdf_fields(pdf_path):
    doc = fitz.open(pdf_path)
    schema = {
        "title": "Detected Court Form",
        "template": pdf_path,
        "pages": len(doc),
        "fields": []
    }

    field_idx = 1
    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()
        
        for draw in drawings:
            for item in draw.get("items", []):
                if item[0] == "l":  # Line
                    p1, p2 = item[1], item[2]
                    # Check if horizontal line (underline)
                    if abs(p1.y - p2.y) < 3 and abs(p1.x - p2.x) > 30:
                        schema["fields"].append({
                            "id": f"field_{field_idx}",
                            "prompt": f"Page {page_num+1} Underline {field_idx}:",
                            "type": "text",
                            "page": page_num + 1,
                            "x": round(p1.x, 1),
                            "y": round(page.rect.height - p1.y + 2, 1),
                            "font_size": 10
                        })
                        field_idx += 1

    return schema

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FormGuide Automated Field Detector")
    parser.add_argument("--input", required=True, help="Path to static input court PDF")
    parser.add_argument("--output", required=True, help="Path to output JSON schema")
    args = parser.parse_args()

    schema = detect_pdf_fields(args.input)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"[+] FormGuide: Detected {len(schema['fields'])} potential form fields. Saved schema to {args.output}")
