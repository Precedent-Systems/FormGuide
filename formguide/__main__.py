#!/usr/bin/env python3
"""
FormGuide Simplified CLI Interface
Usage:
  formguide fill js44 [profile.json] [output.pdf]
  formguide fill ifp [profile.json] [output.pdf]
  formguide map input.pdf [output_schema.json]
  formguide wizard [schema.json]
"""

import sys
import os
import json
import argparse

FORMGUIDE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FORMGUIDE_ROOT)

from formguide.form_mapper import detect_pdf_fields
from formguide.filling_engine import fill_form_with_profile, fill_acroform_pdf

PRESET_SCHEMAS = {
    "js44": {
        "template": os.path.join(FORMGUIDE_ROOT, "templates", "js_044.pdf"),
        "schema": os.path.join(FORMGUIDE_ROOT, "schemas", "federal", "us_district_court_js044.json"),
        "default_out": "JS44_Civil_Cover_Sheet_Filled.pdf"
    },
    "ifp": {
        "template": os.path.join(FORMGUIDE_ROOT, "templates", "Application to Proceed Without Prepayment of Fees or Costs.pdf"),
        "schema": os.path.join(FORMGUIDE_ROOT, "schemas", "federal", "us_district_court_ao240_ifp.json"),
        "default_out": "IFP_Fee_Waiver_Application_Filled.pdf"
    }
}

DEFAULT_PROFILE = os.path.join(FORMGUIDE_ROOT, "profiles", "annika_eriksson_profile.json")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print("\n⚖️ FormGuide Simplified CLI")
        print("--------------------------------------------------")
        print("  formguide fill js44 [profile.json] [out.pdf]   Fill Federal JS 44 Cover Sheet")
        print("  formguide fill ifp  [profile.json] [out.pdf]   Fill Federal IFP Fee Waiver Form")
        print("  formguide map <form.pdf> [schema.json]        Auto-detect & map fields from any PDF")
        print("  formguide wizard                              Run interactive interview")
        print("--------------------------------------------------\n")
        return

    cmd = sys.argv[1].lower()

    if cmd == "fill":
        preset_key = sys.argv[2].lower() if len(sys.argv) > 2 else "js44"
        profile_path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PROFILE
        
        if preset_key in PRESET_SCHEMAS:
            preset = PRESET_SCHEMAS[preset_key]
            out_pdf = sys.argv[4] if len(sys.argv) > 4 else preset["default_out"]
            print(f"🚀 Filling {preset_key.upper()} form using profile: {os.path.basename(profile_path)}")
            
            # Simple direct field mapping
            with open(profile_path, 'r', encoding='utf-8') as f:
                prof = json.load(f)
            
            # Key preset shortcuts
            if preset_key == "js44":
                field_map = {
                    "topmostSubform[0].Page1[0].plaintiffs[0]": prof.get("personal", {}).get("first_name", "") + " " + prof.get("personal", {}).get("last_name", "") + " and " + prof.get("personal", {}).get("co_plaintiff", ""),
                    "topmostSubform[0].Page1[0].defendants[0]": prof.get("litigation", {}).get("defendants", "City of Oregon City, et al."),
                    "topmostSubform[0].Page1[0].plCty[0]": prof.get("personal", {}).get("county", "Clackamas County"),
                    "topmostSubform[0].Page1[0].defCty[0]": prof.get("personal", {}).get("county", "Clackamas County"),
                    "topmostSubform[0].Page1[0].attorneysPL[0]": prof.get("personal", {}).get("first_name", "") + " " + prof.get("personal", {}).get("last_name", "") + " (Pro Se), " + prof.get("personal", {}).get("address", "")
                }
            else:
                field_map = {
                    "plaintiff 1": prof.get("personal", {}).get("first_name", "") + " " + prof.get("personal", {}).get("last_name", ""),
                    "defendant 1": "City of Oregon City, et al.",
                    "Amount of takehome salary or wages": prof.get("financial", {}).get("take_home_pay", "$533.82/period")
                }
            
            fill_acroform_pdf(preset["template"], field_map, out_pdf)
            print(f"✅ Created court PDF: {out_pdf}")
        else:
            print(f"❌ Unknown preset '{preset_key}'. Choose 'js44' or 'ifp'.")

    elif cmd == "map":
        pdf_in = sys.argv[2] if len(sys.argv) > 2 else ""
        if not pdf_in or not os.path.exists(pdf_in):
            print("❌ Please provide a valid input PDF path. Usage: formguide map <form.pdf>")
            return
        schema_out = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(pdf_in)[0] + "_schema.json"
        schema = detect_pdf_fields(pdf_in, os.path.basename(pdf_in))
        with open(schema_out, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        print(f"✅ Generated schema for {os.path.basename(pdf_in)} -> {schema_out}")

    else:
        print(f"Unknown command '{cmd}'. Run 'formguide --help' for options.")

if __name__ == "__main__":
    main()
