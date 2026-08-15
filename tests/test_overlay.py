"""
Test suite for FormGuide overlay engine & reference schema compilation.
"""

import os
import json
import pytest
from formguide.overlay_engine import fill_form_from_answers

def test_notice_of_appeal_compilation():
    schema_path = "/home/annika/FormGuide/schemas/oregon_notice_of_appeal.json"
    output_path = "/home/annika/FormGuide/tests/test_notice_of_appeal_filled.pdf"

    answers = {
        "plaintiff_name": "Annika Eriksson",
        "plaintiff_role": "Plaintiff-Appellant",
        "defendant_name": "The Bank of New York Mellon, et al.",
        "defendant_role": "Defendant-Respondent",
        "circuit_court_county": "Clackamas",
        "circuit_court_case_no": "24CV21417",
        "appellant_name_body": "Annika Eriksson",
        "judgment_date": "08/10/2026",
        "trial_judge_name": "Judge Boutin",
        "filing_date": "08/10/2026",
        "filing_method": "Electronic Filing through the court's eFiling system"
    }

    success = fill_form_from_answers(schema_path, answers, output_path)
    assert success is True
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 10000
