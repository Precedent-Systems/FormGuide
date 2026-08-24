# FormGuide: An Open-Source, Jurisdiction-Agnostic Court Form Automation Toolkit

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)]()
[![Court Grade](https://img.shields.io/badge/Court_Grade-Vector_Precision-gold.svg)]()

**FormGuide** (by Precedent Systems Org) is a free, open-source, serverless Python alternative to expensive proprietary legal form stacks (HotDocs, Lawyaw, Gavel) and jurisdiction-locked state portals.

The toolkit automatically converts any static or interactive court PDF into a reusable JSON Schema, accepts local User Profiles, and populates AcroForms or overlays high-precision vector typography onto official court documents.

---

## 🎯 Architectural Principles & Scope Control

FormGuide follows a **bite-sized, Unix-philosophy architecture**:

```
                       FORMGUIDE 3-TIER ARCHITECTURE
                                     │
   ┌─────────────────────────────────┼─────────────────────────────────┐
   ▼                                 ▼                                 ▼
1. FORM SCHEMA               2. USER PROFILE DATA              3. FILLING & OVERLAY
   (Template Geometry)          (Local Instance Data)             (AcroForm + ReportLab)
   schemas/federal/             profiles/                          formguide/
   us_district_court_js044.json  user_profile.json                  filling_engine.py
```

### 💡 Why Local Profiles > OAuth / SaaS Auth
- **Zero Server Infrastructure:** Storing PII (income, SSNs, medical records, legal claims) in central databases creates privacy liability and compliance bloat.
- **Local-First Privacy:** User Profiles are simple local JSON files (`user_profile.json`). Users keep 100% control of their sensitive legal data on their own machine.
- **Bite-Sized MVP:** Keeps the product lightweight, fast, and dependency-free.

---

## 🏗️ Repository Layout

```
FormGuide/
├── schemas/                           # Reusable Template Geometry Schemas (.json)
│   ├── federal/
│   │   ├── us_district_court_js044.json       # Federal Civil Cover Sheet (139 mapped fields)
│   │   └── us_district_court_ao240_ifp.json   # Federal Form AO 240 IFP Application (93 fields)
│   ├── oregon_notice_of_appeal.json       # Oregon Court of Appeals Notice of Appeal
│   └── oregon_small_claims.json           # Oregon Circuit Court Small Claims Form
├── profiles/                          # Local User Instance Profiles (.json)
│   └── annika_eriksson_profile.json   # Example Litigant Profile
├── formguide/
│   ├── form_mapper.py                 # Auto Field Detection Engine (AcroForms & Underlines)
│   ├── filling_engine.py              # Native AcroForm & Vector Overlay Merger
│   ├── wizard.py                      # Interactive CLI Q&A Interview Engine
│   └── overlay_engine.py              # ReportLab Coordinate Overlay Generator
├── templates/                         # Reference Court PDF Templates
└── README.md
```

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/precedent-systems/FormGuide.git
cd FormGuide
pip install -r requirements.txt
```

### 2. Auto-Map Any New Court PDF (Instant Extensibility)

FormGuide is **automatically extensible to any court form in seconds**. Run `form_mapper.py` against any downloaded PDF to extract field geometry, widget names, and point coordinates:

```bash
python3 -m formguide.form_mapper --input ~/Downloads/my_custom_form.pdf --output schemas/custom/my_form_schema.json
```

### 3. Fill Forms Using a Local User Profile

Merge local profile data onto official PDF templates:

```bash
python3 -m formguide.filling_engine \
  --template ~/Downloads/js_044.pdf \
  --schema schemas/federal/us_district_court_js044.json \
  --profile profiles/annika_eriksson_profile.json \
  --output Filled_JS44_Civil_Cover_Sheet.pdf
```

---

## ⚖️ Differentiation Matrix

| Dimension | Proprietary Tools | State Portals | FormGuide |
|---|---|---|---|
| **Cost** | High Subscription ($100s/mo) | Tax-Funded | **Free, Open-Source (AGPLv3)** |
| **Jurisdiction Lock** | Vendor Ecosystem | Single State | **Any Federal or State PDF** |
| **Data Privacy** | Vendor Cloud SaaS | State Database | **100% Local-First JSON** |
| **Schema Creation** | Vendor/Trained Staff | Court IT Only | **Auto-Generated via `form_mapper`** |

---

## ⚖️ License

Distributed under the **GNU Affero General Public License v3.0 (AGPLv3)**. Free forever for pro se litigants, legal aid organizations, and public defenders.
