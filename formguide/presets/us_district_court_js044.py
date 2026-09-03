#!/usr/bin/env python3
"""
FormGuide JS 44 Civil Cover Sheet Automated Generator & Filler
Pulls profile attributes from FormGuide profile (annika_eriksson_profile.json)
and populates the U.S. District Court JS 44 Civil Cover Sheet template (templates/js_044.pdf).
"""

import sys
import os
import json
import shutil
import fitz  # PyMuPDF

FORMGUIDE_DIR = "/home/annika/FormGuide"
sys.path.insert(0, FORMGUIDE_DIR)

from formguide.filling_engine import fill_acroform_pdf

PROFILE_PATH = os.path.join(FORMGUIDE_DIR, "profiles", "annika_eriksson_profile.json")
TEMPLATE_PATH = os.path.join(FORMGUIDE_DIR, "templates", "js_044.pdf")
OUTPUT_PATH = os.path.join(FORMGUIDE_DIR, "FormGuide_JS44_Civil_Cover_Sheet_FILLED.pdf")
FILE_NEXT_DIR = "/home/annika/google_drive_intake/File_Next"
DESKTOP_FED_DIR = "/home/annika/Desktop/FILE_NOW_CENTRAL_COMMAND/01_FEDERAL_CIVIL_RIGHTS_ACTION"

def build_js44_cover_sheet():
    print(f"🚀 [FormGuide Preset] Building JS 44 Civil Cover Sheet from Profile...")
    if not os.path.exists(PROFILE_PATH):
        raise FileNotFoundError(f"Profile file missing: {PROFILE_PATH}")
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template file missing: {TEMPLATE_PATH}")

    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    personal = profile.get("personal", {})
    litigation = profile.get("litigation", {})

    plaintiff_str = f"{personal.get('first_name')} {personal.get('last_name')} & {personal.get('co_plaintiff')}"
    defendant_str = litigation.get("defendants", "City of Oregon City, Tony Konkol, Ramon Henderson, Alexandra Troutman, Ashley Fraijo, John Oreskovich, Vance Walker")
    attorney_str = f"{plaintiff_str} (Pro Se), 12054 Chapin Ct., Oregon City, OR 97045, (503) 555-0199"

    field_values = {
        # Section I: Parties & Counties
        "topmostSubform[0].Page1[0].plaintiff[0]": plaintiff_str,
        "topmostSubform[0].Page1[0].defendant[0]": defendant_str,
        "topmostSubform[0].Page1[0].county1[0]": personal.get("county", "Clackamas County"),
        "topmostSubform[0].Page1[0].county2[0]": "Clackamas County",
        "topmostSubform[0].Page1[0].attorneys[0]": attorney_str,
        "topmostSubform[0].Page1[0].defAttorneys[0]": "Unknown / City Attorney's Office, City of Oregon City, 625 Center St, Oregon City, OR 97045",

        # Section II: Basis of Jurisdiction (3 = Federal Question -> Export State '2')
        "topmostSubform[0].Page1[0].q2[0]": "2",

        # Section IV: Nature of Suit (440 Civil Rights: Other -> Export State '35')
        "topmostSubform[0].Page1[0].q4[0]": "35",

        # Section V: Origin (1. Original Proceeding -> Export State '0')
        "topmostSubform[0].Page1[0].q5[0]": "0",

        # Section VI: Cause of Action & Statute
        "topmostSubform[0].Page1[0].S6stat[0]": litigation.get("primary_statute", "42 U.S.C. §§ 1983, 12132"),
        "topmostSubform[0].Page1[0].S6cause[0]": litigation.get("cause_of_action", "Civil rights: municipal water shutoff, ADA accommodation denial, property seizure under color of law"),

        # Section VII: Requested in Complaint
        "topmostSubform[0].Page1[0].S7demand[0]": "$75,000",
        "topmostSubform[0].Page1[0].classAction[0]": "Off",
        "topmostSubform[0].Page1[0].jury[0]": "0",  # 0 = Yes for Jury Demand

        # Section VIII: Related Cases
        "topmostSubform[0].Page1[0].S8judge[0]": "N/A",
        "topmostSubform[0].Page1[0].S8docket[0]": "N/A",

        # Date & Signature
        "topmostSubform[0].Page1[0].date[0]": "September 3, 2026",
        "topmostSubform[0].Page1[0].sig[0]": f"{plaintiff_str} (Pro Se)"
    }

    fill_acroform_pdf(TEMPLATE_PATH, field_values, OUTPUT_PATH)

    # Sync to File_Next
    os.makedirs(FILE_NEXT_DIR, exist_ok=True)
    dest_path1 = os.path.join(FILE_NEXT_DIR, "FORMGUIDE_JS44_CIVIL_COVER_SHEET_FILLED.pdf")
    shutil.copy(OUTPUT_PATH, dest_path1)

    # Sync to Desktop 02_FEDERAL_CIVIL_RIGHTS_CASE
    os.makedirs(DESKTOP_FED_DIR, exist_ok=True)
    dest_path2 = os.path.join(DESKTOP_FED_DIR, "FORMGUIDE_JS44_CIVIL_COVER_SHEET_FILLED.pdf")
    shutil.copy(OUTPUT_PATH, dest_path2)

    print(f"✅ Generated & synced JS 44 Cover Sheet to:\n   - {dest_path1}\n   - {dest_path2}")
    return dest_path2

if __name__ == "__main__":
    build_js44_cover_sheet()
