"""
Test suite for FormGuide overlay engine & Small Claims schema compilation.
"""

import os
import json
import pytest
from formguide.overlay_engine import fill_form_from_answers

def test_small_claims_compilation():
    schema_path = "/home/annika/FormGuide/schemas/oregon_small_claims.json"
    output_path = "/home/annika/FormGuide/tests/test_small_claims_filled.pdf"

    answers = {
        "plaintiff_name": "Annika Eriksson",
        "plaintiff_address": "12054 Chapin Ct., Oregon City, OR 97045",
        "defendant_name": "City of Oregon City",
        "defendant_address": "625 Center St., Oregon City, OR 97045",
        "circuit_court_county": "Clackamas",
        "case_number": "26SC99999",
        "claim_amount": "10000.00",
        "claim_reason": "Unlawful utility shutoff and administrative fee overcharges.",
        "declaration_date": "08/14/2026",
        "declarant_signature_name": "Annika Eriksson"
    }

    success = fill_form_from_answers(schema_path, answers, output_path)
    assert success is True
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 10000
