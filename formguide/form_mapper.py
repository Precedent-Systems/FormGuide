"""
FormGuide Field Detection & Schema Generator Engine
Analyzes static or interactive court PDFs to auto-extract AcroForm fields, text boundaries, and drawn underlines.
Outputs jurisdiction-agnostic, human-editable JSON form schemas.
"""

import argparse
import json
import os
import fitz  # PyMuPDF

import argparse
import json
import os
import re
import fitz  # PyMuPDF

def _extract_nearby_label(page_words, rect):
    """
    Extracts text label to the left or above the target bounding box.
    """
    nearby = []
    for wd in page_words:
        wx0, wy0, wx1, wy1, word = wd[0], wd[1], wd[2], wd[3], wd[4]
        # Text to the left on the same line (+/- 8pt Y band)
        if abs(wy0 - rect.y0) < 10 and (rect.x0 - wx1) >= -5 and (rect.x0 - wx1) < 220:
            nearby.append((wy0, wx0, word))
        # Text directly above within 18pt
        elif (wy1 <= rect.y0 + 2) and (rect.y0 - wy1 < 18) and (wx0 >= rect.x0 - 40) and (wx1 <= rect.x1 + 40):
            nearby.append((wy0, wx0, word))
    nearby.sort(key=lambda item: (round(item[0]/5)*5, item[1]))
    raw = " ".join([n[2] for n in nearby])
    cleaned = re.sub(r'[_~]+', '', raw).strip()
    return cleaned

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
        words = page.get_text("words")
        
        # 1. Extract Native AcroForm Widgets
        widgets = list(page.widgets())
        for w in widgets:
            fid = w.field_name or f"widget_{field_idx}"
            if fid in seen_field_ids:
                fid = f"{fid}_{field_idx}"
            seen_field_ids.add(fid)

            rect = w.rect
            x0 = round(rect.x0, 1)
            y0 = round(page_height - rect.y1, 1)
            w_width = round(rect.width, 1)
            w_height = round(rect.height, 1)

            ftype = "text"
            if w.field_type_string in ["CheckBox", "RadioButton"]:
                ftype = "choice"
            elif w.field_type_string == "ComboBox":
                ftype = "select"

            label = _extract_nearby_label(words, rect)
            prompt = f"Page {page_num+1} - {label}" if label else f"Page {page_num+1} ({fid}):"

            schema["fields"].append({
                "id": fid,
                "prompt": prompt,
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

        # 2. Extract Vector Underlines & Rectangles (if widgets absent or incomplete)
        if not widgets or len(widgets) < 3:
            drawings = page.get_drawings()
            for draw in drawings:
                for item in draw.get("items", []):
                    if item[0] in ["l", "re"]:  # Line or rectangle
                        if item[0] == "l":
                            p1, p2 = item[1], item[2]
                            is_horiz = abs(p1.y - p2.y) < 4 and abs(p1.x - p2.x) > 25
                            x0 = round(min(p1.x, p2.x), 1)
                            y0 = round(page_height - max(p1.y, p2.y) + 2, 1)
                            w_width = round(abs(p1.x - p2.x), 1)
                            r_rect = fitz.Rect(x0, min(p1.y, p2.y) - 10, x0 + w_width, max(p1.y, p2.y) + 5)
                        else:
                            r = item[1]
                            is_horiz = r.height < 25 and r.width > 25
                            x0 = round(r.x0, 1)
                            y0 = round(page_height - r.y1, 1)
                            w_width = round(r.width, 1)
                            r_rect = r

                        if is_horiz:
                            label = _extract_nearby_label(words, r_rect)
                            fid = label.lower().replace(" ", "_") if label else f"underline_{field_idx}"
                            if fid in seen_field_ids:
                                fid = f"{fid}_{field_idx}"
                            seen_field_ids.add(fid)

                            schema["fields"].append({
                                "id": fid,
                                "prompt": f"Page {page_num+1} ({label or fid}):",
                                "type": "text",
                                "page": page_num + 1,
                                "x": x0,
                                "y": y0,
                                "width": w_width,
                                "font_size": 10
                            })
                            field_idx += 1

        # 3. Fallback: Text Colon Prompt Detection for Flat Forms
        if not widgets and not schema["fields"]:
            blocks = page.get_text("blocks")
            for b in blocks:
                b_text = b[4].strip()
                for line in b_text.splitlines():
                    line = line.strip()
                    if ":" in line and len(line) < 60:
                        prompt_label = line.split(":")[0].strip()
                        fid = re.sub(r'[^a-zA-Z0-9_]', '', prompt_label.lower().replace(' ', '_'))
                        if fid and fid not in seen_field_ids:
                            seen_field_ids.add(fid)
                            schema["fields"].append({
                                "id": fid,
                                "prompt": f"Page {page_num+1} ({prompt_label}):",
                                "type": "text",
                                "page": page_num + 1,
                                "x": round(b[0] + 120, 1),
                                "y": round(page_height - b[3], 1),
                                "width": 200,
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

