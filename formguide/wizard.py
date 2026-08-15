"""
FormGuide Interactive Wizard Engine
Presents plain-English questions to the user and generates a filled court-compliant PDF.
"""

import json
import argparse
from formguide.overlay_engine import fill_form_from_answers

def run_cli_interview(schema_path):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_data = json.load(f)

    print(f"\n========================================================")
    print(f"  FormGuide Wizard: {schema_data.get('title', 'Court Form')}")
    print(f"  Jurisdiction: {schema_data.get('jurisdiction', 'General')}")
    print(f"========================================================\n")

    answers = {}
    for field in schema_data.get("fields", []):
        field_id = field.get("id")
        prompt = field.get("prompt", field_id)
        choices = field.get("choices")

        if choices:
            print(f"\n{prompt}")
            for idx, choice in enumerate(choices, 1):
                print(f"  [{idx}] {choice}")
            ans_idx = input("Select option number: ").strip()
            try:
                answers[field_id] = choices[int(ans_idx) - 1]
            except Exception:
                answers[field_id] = choices[0]
        else:
            val = input(f"{prompt} ").strip()
            answers[field_id] = val

    return answers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FormGuide Court Form Wizard")
    parser.add_argument("--schema", required=True, help="Path to FormGuide JSON schema file")
    parser.add_argument("--output", required=True, help="Path to output filled PDF")
    args = parser.parse_args()

    user_answers = run_cli_interview(args.schema)
    fill_form_from_answers(args.schema, user_answers, args.output)
