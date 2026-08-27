"""
FormGuide Production Filling Engine
Fills court PDF templates using mapped AcroForm widget names:
  - Text fields: set string value
  - CheckBox fields: set True/False (or "Yes"/"No"/1/0 aliases)
  - RadioButton groups: set the export value string (e.g. "3") to select a specific button
"""

import os
import json
import fitz  # PyMuPDF

# Truthy aliases for checkbox fields
_CHECKBOX_ON  = {"true", "yes", "1", "on", "x", "checked"}
_CHECKBOX_OFF = {"false", "no", "0", "off", "", "unchecked"}


def _coerce_checkbox(val) -> bool:
    """Return True if val means 'checked'."""
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        return val != 0
    return str(val).strip().lower() in _CHECKBOX_ON


def fill_acroform_pdf(template_path, field_values, output_path):
    """
    Fills native AcroForm fields in PDF using PyMuPDF.

    field_values is a dict keyed by AcroForm field name.  Values:
      - Text fields   → any str
      - CheckBox      → bool or truthy/falsy alias string
      - RadioButton   → the export string of the button to select (e.g. "3")
                        OR a human label if a label→export mapping is provided
                        via a "~radio_labels" sub-key in field_values:
                          field_values["~radio_labels"] = {
                              "field_name": {"label": "export_val", ...}
                          }
    """
    doc = fitz.open(template_path)

    # Optional label→export-value lookup for radio groups
    radio_labels = field_values.pop("~radio_labels", {})

    filled_text  = 0
    filled_check = 0
    filled_radio = 0
    skipped      = 0

    for page in doc:
        for w in page.widgets():
            fname = w.field_name
            if fname not in field_values:
                continue

            raw_val = field_values[fname]
            ftype   = w.field_type_string  # 'Text', 'CheckBox', 'RadioButton', etc.

            try:
                if ftype == "CheckBox":
                    checked = _coerce_checkbox(raw_val)
                    w.field_value = "Yes" if checked else "Off"
                    w.update()
                    filled_check += 1

                elif ftype == "RadioButton":
                    # Resolve label → export value if a mapping was given
                    export_val = str(raw_val)
                    if fname in radio_labels:
                        export_val = radio_labels[fname].get(str(raw_val), export_val)
                    # PyMuPDF: set the whole radio group to the given export value
                    w.field_value = export_val
                    w.update()
                    filled_radio += 1

                else:
                    # Text, Combo, ListBox, etc.
                    w.field_value = str(raw_val)
                    w.update()
                    filled_text += 1

            except Exception as e:
                print(f"  ⚠️  [{ftype}] {fname!r}: {e}")
                skipped += 1

    doc.save(output_path)
    print(f"✅ [FormGuide Engine] Text={filled_text}  CheckBox={filled_check}  Radio={filled_radio}  Skipped={skipped}")
    print(f"📄 Saved: {output_path}")

    # Restore in case caller reuses dict
    if radio_labels:
        field_values["~radio_labels"] = radio_labels

    return output_path


def fill_form_with_profile(template_path, schema_path, profile_path, field_mapping, output_path):
    """
    Maps profile JSON attributes to schema field IDs/names and fills the target PDF.
    field_mapping: { acro_name: "profile.dot.path" }
    """
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    field_values = {}
    for acro_name, profile_key in field_mapping.items():
        val = profile
        for part in profile_key.split('.'):
            if isinstance(val, dict):
                val = val.get(part, "")
            else:
                break
        if val != "":
            field_values[acro_name] = val  # preserve bool for checkboxes

    return fill_acroform_pdf(template_path, field_values, output_path)
