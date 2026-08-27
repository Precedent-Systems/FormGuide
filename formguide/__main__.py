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
            lit  = prof.get("litigation", {})
            pers = prof.get("personal", {})
            fin  = prof.get("financial", {})

            if preset_key == "js44":
                pl_name  = f"{pers.get('first_name','')} {pers.get('last_name','')} and {pers.get('co_plaintiff','')}".strip()
                pro_se   = f"{pers.get('first_name','')} {pers.get('last_name','')} (Pro Se), {pers.get('address','')}, {pers.get('city','')}, {pers.get('state','')} {pers.get('zip','')}".strip()

                field_map = {
                    # Section I — Parties
                    "topmostSubform[0].Page1[0].plaintiffs[0]":   pl_name,
                    "topmostSubform[0].Page1[0].defendants[0]":   lit.get("defendants", "City of Oregon City, et al."),
                    "topmostSubform[0].Page1[0].plCty[0]":        pers.get("county", "Clackamas County"),
                    "topmostSubform[0].Page1[0].defCty[0]":       pers.get("county", "Clackamas County"),
                    "topmostSubform[0].Page1[0].attorneysPL[0]":  pro_se,

                    # Section II — Basis of Jurisdiction (RadioButton export value)
                    # 1=US Govt Pl, 2=US Govt Def, 3=Fed Question, 4=Diversity
                    "topmostSubform[0].Page1[0].q2[0]":           lit.get("jurisdiction_basis_code", "3"),

                    # Section III — Citizenship (checkboxes S3P1–S3P6, S3D1–S3D6)
                    # For federal question suits these are typically left blank
                    # (set them explicitly in profile if needed)

                    # Section V — Origin (RadioButton export value: "1" = Original Filing)
                    "topmostSubform[0].Page1[0].q4[0]":           lit.get("origin_code", "1"),

                    # Section V — Class Action checkbox
                    "topmostSubform[0].Page1[0].classAction[0]":  lit.get("class_action", False),

                    # Section V — Related case (RadioButton: "0"=No, "1"=Yes)
                    "topmostSubform[0].Page1[0].q5[0]":           lit.get("related_case", "0"),

                    # Section VI — Cause of Action
                    "topmostSubform[0].Page1[0].S6stat[0]":       lit.get("primary_statute", "42 U.S.C. §§ 1983, 12132"),
                    "topmostSubform[0].Page1[0].S6cause[0]":      lit.get("cause_of_action", "Civil rights violation under color of law"),

                    # Section VII — Jury demand (RadioButton: "1"=Yes, "2"=No)
                    "topmostSubform[0].Page1[0].jury[0]":         "1" if lit.get("jury_demand", True) else "2",

                    # Section VII — Demand amount
                    "topmostSubform[0].Page1[0].S7demand[0]":     lit.get("demand_dollars", "75000"),

                    # Date & signature
                    "topmostSubform[0].Page1[0].date[0]":         __import__("datetime").date.today().strftime("%m/%d/%Y"),
                    "topmostSubform[0].Page1[0].sig[0]":          f"{pers.get('first_name','')} {pers.get('last_name','')} (Pro Se)",
                }
            else:
                field_map = {
                    "plaintiff 1": f"{pers.get('first_name','')} {pers.get('last_name','')}",
                    "defendant 1": "City of Oregon City, et al.",
                    "Amount of takehome salary or wages": fin.get("take_home_pay", "$533.82/period")
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
