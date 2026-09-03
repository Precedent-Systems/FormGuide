#!/usr/bin/env python3
"""
FormGuide AO 240 IFP Application Automated Generator & Filler
Pulls profile attributes from FormGuide profile (annika_eriksson_profile.json)
and populates the U.S. District Court AO 240 IFP Application template.
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
TEMPLATE_PATH = os.path.join(FORMGUIDE_DIR, "templates", "Application to Proceed Without Prepayment of Fees or Costs.pdf")
OUTPUT_PATH = os.path.join(FORMGUIDE_DIR, "FormGuide_AO240_IFP_Application_FILLED.pdf")
FILE_NEXT_DIR = "/home/annika/google_drive_intake/File_Next"

def build_single_ifp(profile_path, out_filename):
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile file missing: {profile_path}")
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template file missing: {TEMPLATE_PATH}")

    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    personal = profile.get("personal", {})
    litigation = profile.get("litigation", {})
    financial = profile.get("financial", {})
    expenses = financial.get("monthly_expenses", {})

    is_employed = financial.get("take_home_pay", "$0.00") != "$0.00"

    field_values = {
        # Caption & Heading
        "Division": "Portland",
        "plaintiff 1": f"{personal.get('first_name')} {personal.get('last_name')}",
        "plaintiff 2": personal.get("co_plaintiff", ""),
        "case number": litigation.get("case_number", "[Pending]"),
        "defendant 1": "City of Oregon City, et al.",
        "defendant 2": "Tony Konkol, Ramon Henderson, et al.",
        "name": f"{personal.get('first_name')} {personal.get('last_name')}",

        # Page 1: Q1 Incarceration (Not incarcerated -> Check 'No')
        "Are you currently incarcerated": "No",
        "place of incarceration": "N/A — APPLICANT IS NOT INCARCERATED",

        # Page 1: Q2 Current Employment
        "Are you currently employed": "Yes_2" if is_employed else "No_2",
        "Employers address": f"{financial.get('employer', 'Patricia Clarke')}, {financial.get('employer_address', '2220 Gilman Ave, Oregon City, OR 97045')} (State of Oregon DHS)" if is_employed else "N/A — UNEMPLOYED",
        "specify pay period": financial.get("hours_per_pay_period", "32 hrs / 2-week pay period") if is_employed else "N/A",
        "Amount of takehome pay or wages": financial.get("take_home_pay", "$0.00") if is_employed else "$0.00",
        "pay period": "2-week pay period" if is_employed else "N/A",

        # Page 2: Q2 Employment Checkboxes & Employer Details
        "Yes_3": "On" if is_employed else "Off",
        "No_3": "Off" if is_employed else "On",
        "Selfemployed_2": "Off",
        "Not applicable": "Off",
        "Name of last employer": "N/A — Currently Employed Part-Time" if is_employed else "N/A — Unemployed",
        "Address of last employer": "N/A",
        "Date of last employment": "N/A",
        "Amount of takehome salary or wages": "N/A",
        "per_2": "N/A",
        "Employers name": financial.get("employer", "Patricia Clarke") if is_employed else "N/A",
        "Employers address_2": financial.get("employer_address", "2220 Gilman Ave, Oregon City, OR 97045") if is_employed else "N/A",
        "spouse take home amount": "N/A — Single Applicant",
        "spouse pay period": "N/A",
        "If the answer is Yes please explain below 1": (
            f"Employer: {financial.get('employer')} (Consumer of Services, State of Oregon DHS Home Care). "
            f"Gross pay: {financial.get('gross_pay')}. Net biweekly take-home: {financial.get('take_home_pay')}. "
            f"Deductions: {financial.get('payroll_deductions', 'Standard withholdings')}. "
            "Applicant is employed part-time as a home care worker, NOT self-employed."
        ) if is_employed else "Applicant is unemployed / disabled with $0.00 earned wages.",
        "If the answer is No please explain below 1": "N/A",

        # Page 2/3 Income checkboxes & values
        "employed": "Yes_6" if is_employed else "No_6",
        "earned received": financial.get("take_home_pay", "$0.00") if is_employed else "$0.00",
        "earned expected": financial.get("take_home_pay", "$0.00") if is_employed else "$0.00",
        "passive": "No_7",
        "passive received": "$0.00",
        "passive expected": "$0.00",
        "Pensions annuities or life insurance payments": "No_8",
        "pension received": "$0.00",
        "pension expected": "$0.00",
        "Disability or workers compensation payments": "No_9",
        "workers comp received": "$0.00",
        "workers comp expected": "$0.00",
        "gifts": "No_10",
        "gifts received": "$0.00",
        "gifts expected": "$0.00",
        "other": "No_11",
        "Source": "N/A",
        "other received": "$0.00",
        "other expected": "$0.00",

        # Page 3 Assets
        "Do you have cash or checking or savings accounts": "Yes_12",
        "If Yes state the total amount": financial.get("cash_assets", "< $100.00"),
        "other valuable property": "No_13",
        "Do you have any other assets": "No_14",
        "If Yes describe the assets and state the value of each asset listed 1": financial.get("savings_and_pto_notes", "No real estate equity or liquid savings reserve."),

        # Page 4 Monthly Expenses & Obligations
        "expenses": "Yes_15",
        "If AYes describe and provide the amount of the monthly expense 1": (
            f"Housing: {expenses.get('housing', '$0.00')}; "
            f"Medical: {expenses.get('medical', '$180/mo')}; "
            f"Food & Utilities: {expenses.get('utilities_food', '$450/mo')}. "
            "Total essential living expenses exceed net income."
        ),
        "relationship to each person and indicate how much you contribute to their support 1": "No financial dependents.",
        "Do you have any debts or financial obligations": "Yes_16",
        "If AYes describe the amounts owed and to whom they are payable 1": (
            "Litigation expenses, quiet title defense liabilities, and accrued municipal surcharges "
            "resulting from Defendant City's 510-day illegal water shutoff."
        ),
        "hardship_statement": financial.get("hardship_statement", ""),
        "DATE": "September 3, 2026",

        # Page 5 Prisoner Account Certification (NOT APPLICABLE)
        "name_88": "NOT APPLICABLE — APPLICANT IS NOT INCARCERATED",
        "sum": "N/A",
        "bank": "N/A — NOT INCARCERATED",
        "balance": "N/A",
        "average": "N/A",
        "DATE_2": "N/A"
    }

    tmp_out = os.path.join(FORMGUIDE_DIR, out_filename)
    fill_acroform_pdf(TEMPLATE_PATH, field_values, tmp_out)

    os.makedirs(FILE_NEXT_DIR, exist_ok=True)
    dest_path = os.path.join(FILE_NEXT_DIR, out_filename)
    shutil.copy(tmp_out, dest_path)

    # Sync to Desktop 02_FEDERAL_CIVIL_RIGHTS_CASE
    desktop_fed = os.path.expanduser("~/Desktop/FILE_NOW_CENTRAL_COMMAND/01_FEDERAL_CIVIL_RIGHTS_ACTION")
    os.makedirs(desktop_fed, exist_ok=True)
    shutil.copy(tmp_out, os.path.join(desktop_fed, out_filename))

    print(f"✅ Generated & synced: {dest_path}")
    return dest_path

def build_ao240_ifp():
    print(f"🚀 [FormGuide Preset] Building AO 240 IFP Applications for BOTH Co-Plaintiffs...")
    annika_prof = os.path.join(FORMGUIDE_DIR, "profiles", "annika_eriksson_profile.json")
    donald_prof = os.path.join(FORMGUIDE_DIR, "profiles", "donald_buckhout_profile.json")

    p1 = build_single_ifp(annika_prof, "FORMGUIDE_AO240_IFP_ANNIKA_ERIKSSON_FILLED.pdf")
    p2 = build_single_ifp(donald_prof, "FORMGUIDE_AO240_IFP_DONALD_BUCKHOUT_FILLED.pdf")

    # Maintain backwards compatible alias
    shutil.copy(p1, os.path.join(FILE_NEXT_DIR, "FORMGUIDE_AO240_IFP_APPLICATION_FILLED.pdf"))
    return [p1, p2]

if __name__ == "__main__":
    build_ao240_ifp()


