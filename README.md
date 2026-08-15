# FormGuide: An Open-Source, Jurisdiction-Agnostic Court Form Automation Toolkit

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)]()
[![Court Grade](https://img.shields.io/badge/Court_Grade-Vector_Precision-gold.svg)]()

**FormGuide** is a free, self-hostable, pure-Python alternative to proprietary court-form automation stacks (A2J Author/HotDocs, Gavel, Lawyaw) and jurisdiction-locked state "Guide & File" portals. 

The toolkit converts any static court PDF into an interactive step-by-step interview, then overlays crisp vector typography onto the original form at precise coordinates.

---

## 🎯 Why This Matters

Existing court-form solutions create friction in three ways:

1. **Proprietary platforms** (Gavel, Lawyaw, HotDocs/LHI) require expensive subscriptions, vendor lock-in, and proprietary template formats.
2. **State-maintained portals** are jurisdiction-specific, funded unpredictably, and rarely cover appellate or specialized forms.
3. **Raw AI filling** lacks reproducible precision; clerks reject misaligned or inconsistent filings.

**FormGuide occupies the gap: court-grade precision without proprietary infrastructure.**

---

## 📊 Differentiation Matrix

| Dimension | Proprietary Tools | State Portals | FormGuide |
|---|---|---|---|
| **Cost** | High Subscription | Free (tax-funded) | **Free, open-source (AGPLv3)** |
| **Jurisdiction Lock** | Vendor ecosystem | Single state | **Any PDF, any court** |
| **Dependencies** | HotDocs, cloud SaaS | State IT budgets | **Pure Python (`pypdf`, `reportlab`)** |
| **Schema Editing** | Vendor/trained staff | Court IT only | **Human-readable JSON** |

---

## 🏗️ Architecture & Component Overview

```
FormGuide/
├── schemas/                           # Editable Form Field Coordinates & Questions (.json)
│   ├── oregon_notice_of_appeal.json   # Reference Implementation: Oregon Court of Appeals
│   └── oregon_small_claims.json       # Oregon Circuit Court Small Claims Packet
├── formguide/
│   ├── form_mapper.py                 # Automated PDF Underline & Field Detection Engine
│   ├── wizard.py                      # Interactive Plain-English Q&A Interview Engine
│   └── overlay_engine.py              # High-Precision ReportLab Vector Overlay Generator
├── templates/                         # Static Court PDF Templates
│   └── oregon_notice_of_appeal_template.pdf
└── README.md
```

- **`form_mapper.py`**: Uses `pypdf`/`pdfplumber` + computer vision to detect underlines, checkboxes, and text bounds on any static PDF. Outputs an editable JSON schema.
- **`wizard.py`**: Interactive CLI/Web interview engine. Converts plain-English user answers into structured data without requiring pixel knowledge.
- **`overlay_engine.py`**: `reportlab`/`pypdf` coordinate overlay engine. Merges vector text directly onto the underlying PDF at exact point coordinates.

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/YourUsername/FormGuide.git
cd FormGuide
pip install -r requirements.txt
```

### 2. Run the Interactive Notice of Appeal Wizard

Generate an e-filing ready Oregon Court of Appeals Notice of Appeal:

```bash
python3 -m formguide.wizard --schema schemas/oregon_notice_of_appeal.json --output Oregon_Notice_of_Appeal_Filled.pdf
```

### 3. Automatically Map Any New Court PDF

Detect underlines and form fields on a new static PDF:

```bash
python3 -m formguide.form_mapper --input templates/my_court_form.pdf --output schemas/my_court_form.json
```

---

## ⚖️ License

Distributed under the **GNU Affero General Public License v3.0 (AGPLv3)**. Free forever for pro se litigants, legal aid organizations, and public defenders.
