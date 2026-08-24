"""
FormGuide Production Filling Engine
Fills court PDF templates using mapped AcroForm widget names or ReportLab point coordinates,
mapping reusable User Profile data onto Form Schema field definitions.
"""

import os
import json
import fitz  # PyMuPDF

def fill_acroform_pdf(template_path, field_values, output_path):
    """
    Fills native AcroForm fields in PDF using PyMuPDF and updates widget appearances.
    """
    doc = fitz.open(template_path)
    
    filled_count = 0
    for page in doc:
        for w in page.widgets():
            fname = w.field_name
            if fname in field_values:
                val = str(field_values[fname])
                w.field_value = val
                w.update()
                filled_count += 1

    doc.save(output_path)
    print(f"✅ [FormGuide Engine] Filled {filled_count} native AcroForm fields.")
    print(f"📄 Saved Filled PDF: {output_path}")
    return output_path

def fill_form_with_profile(template_path, schema_path, profile_path, field_mapping, output_path):
    """
    Maps profile JSON attributes to schema field IDs/names and fills the target PDF.
    """
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    # Resolve field values
    field_values = {}
    for acro_name, profile_key in field_mapping.items():
        # Traverse profile dict (e.g. "personal.first_name")
        val = profile
        for part in profile_key.split('.'):
            if isinstance(val, dict):
                val = val.get(part, "")
            else:
                break
        if val:
            field_values[acro_name] = str(val)

    return fill_acroform_pdf(template_path, field_values, output_path)
