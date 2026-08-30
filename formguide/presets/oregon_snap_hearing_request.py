#!/usr/bin/env python3
"""
Generate a filled OAR 137-003-0001 Compliant Petition for Contested Case Hearing
and Request for Aid Pending for SNAP/Benefits.

Usage:
    python3 generate_snap_hearing.py

Output:
    Oregon_SNAP_Contested_Hearing_Request_FILLED.pdf
"""

import sys, os, datetime
sys.path.insert(0, '/home/annika/FormGuide')

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUTPUT = os.path.expanduser(
    '~/case-workspace/epa-complaint/deliverables/Oregon_SNAP_Contested_Hearing_Request_FILLED.pdf'
)
FILE_NEXT = os.path.expanduser('~/google_drive_intake/File_Next/')

# ── Debtor / Client profile ──────────────────────────────────────────────────
DEBTOR = {
    'name':       'Annika U. Eriksson',
    'address':    '12054 Chapin Ct.',
    'city_state': 'Oregon City, OR 97045',
    'phone':      '(503) 555-0199',
    'case_no':    '[Insert ODHS Case / Client ID Number]',
}

TODAY = datetime.date.today().strftime('%B %d, %Y')
TODAY_SHORT = datetime.date.today().strftime('%m/%d/%Y')

def hline(c, x1, x2, y, width=0.5, color=colors.black):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)

def label_field(c, label, value, x, y, label_width=130, font_size=9):
    c.setFont('Helvetica-Bold', font_size)
    c.drawString(x, y, label)
    c.setFont('Helvetica', font_size)
    c.drawString(x + label_width, y, value)

def wrapped_text(c, text, x, y, max_width, font='Helvetica', size=8.5, leading=12):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words = text.split()
    lines = []
    line = ''
    for word in words:
        test = (line + ' ' + word).strip()
        if stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    c.setFont(font, size)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y

def build(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=letter)
    W, H = letter
    m = 0.75 * inch   # margin
    rw = W - 2 * m    # usable width

    # ── PAGE 1 ────────────────────────────────────────────────────────────────
    y = H - 0.6 * inch

    # Header
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(W/2, y, 'STATE OF OREGON')
    y -= 14
    c.drawCentredString(W/2, y, 'DEPARTMENT OF HUMAN SERVICES (ODHS)')
    y -= 16
    hline(c, m, W-m, y, 1.5)
    y -= 20

    # Caption Box (Model Rule Format)
    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(m, y, 'In the Matter of the Public Assistance Benefits of:')
    c.drawRightString(W-m, y, 'PETITION FOR CONTESTED CASE HEARING')
    y -= 13
    c.setFont('Helvetica', 9.5)
    c.drawString(m + 15, y, DEBTOR['name'] + ',')
    c.setFont('Helvetica-Bold', 9)
    c.drawRightString(W-m, y, 'AND REQUEST FOR AID PENDING')
    y -= 13
    c.setFont('Helvetica', 9.5)
    c.drawString(m + 15, y, 'Petitioner / Client.')
    c.setFont('Helvetica-Bold', 9)
    c.drawRightString(W-m, y, f'Case No. {DEBTOR["case_no"]}')
    y -= 8
    hline(c, m, W-m, y, 1.5)
    y -= 20

    # Section 1: Hearing Request
    c.setFont('Helvetica-Bold', 10)
    c.drawString(m, y, 'I. REQUEST FOR HEARING (OAR 137-003-0001 & OAR 461-025-0310)')
    y -= 14
    intro = (
        f'Petitioner {DEBTOR["name"]} hereby requests a Contested Case Hearing before '
        'the Office of Administrative Hearings (OAH) to appeal the recent reduction and '
        're-determination of Petitioner\'s SNAP food benefits and public assistance levels.'
    )
    y = wrapped_text(c, intro, m, y, rw, size=9, leading=13)
    y -= 16

    # Section 2: Request for Aid Pending
    c.setFont('Helvetica-Bold', 10)
    c.drawString(m, y, 'II. REQUEST FOR INTERIM AID PENDING HEARING (OAR 461-025-0310)')
    y -= 14
    aid_pending = (
        'Pursuant to Oregon Administrative Rules (OAR) 461-025-0310 and federal regulations '
        'under 7 CFR § 273.15(p), Petitioner requests that public assistance and SNAP benefits '
        'be immediately restored to their full prior level on an interim basis. Because this '
        'hearing request is filed timely within the statutory period, Petitioner is legally entitled '
        'to the maintenance of benefits ("Aid Pending") until a final hearing decision is issued.'
    )
    y = wrapped_text(c, aid_pending, m, y, rw, size=9, leading=13)
    y -= 16

    # Section 3: Issues and Exemption Claims
    c.setFont('Helvetica-Bold', 10)
    c.drawString(m, y, 'III. ISSUES IN DISPUTE & DETAILED CLARIFICATIONS')
    y -= 14

    issues = [
        ('1. SEPARATE HOUSEHOLD STATUS (OAR 461-135-0500)',
         'Petitioner resides at 12054 Chapin Court but customarily purchases and prepares all '
         'food and meals separately from other occupants in the structure. Under OAR 461-135-0500 '
         'and 7 CFR § 273.1(a)(2), this separate food preparation structure qualifies Petitioner '
         'as an independent SNAP household. The income, assets, and expenses of other household '
         'members must be excluded from Petitioner\'s benefit calculation.'),

        ('2. PROPERTY TAXES AS AN ACCRUED SHELTER EXPENSE (OAR 461-160-0430)',
         'Petitioner is the record owner of the dwelling. Although the mortgage servicer advanced '
         'property tax disbursements during active quiet title and foreclosure litigation, these '
         'disbursements are billed directly to Petitioner and accrue as an active debt liability '
         'against the property. Under OAR 461-160-0430 and 7 CFR § 273.9(d)(6)(ii)(C), property '
         'taxes must be budgeted as a shelter expense. These are not vendor gifts or income; they '
         'constitute an accrued housing liability for which Petitioner remains legally responsible.'),

        ('3. FULL STANDARD UTILITY ALLOWANCE (SUA) DEDUCTION (OAR 461-160-0550)',
         'Petitioner pays out-of-pocket utility expenses at this residence, including heating '
         '(natural gas via NW Natural) and cooling/electricity (via PGE). Under OAR 461-160-0550, '
         'paying for heating/cooling costs automatically entitles Petitioner\'s household to the '
         'Full Standard Utility Allowance (SUA). Petitioner request that this deduction be applied.'),
    ]

    for title, body in issues:
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(m + 10, y, title)
        y -= 12
        y = wrapped_text(c, body, m + 20, y, rw - 20, size=8.5, leading=12)
        y -= 12

    # Declaration
    hline(c, m, W-m, y+4, 0.5, colors.HexColor('#888888'))
    y -= 8
    c.setFont('Helvetica-Bold', 9)
    c.drawString(m, y, 'DECLARATION & SIGNATURE')
    y -= 13
    decl = (
        'I declare under penalty of perjury under the laws of the State of Oregon that the '
        'foregoing statements are true and correct to the best of my knowledge.'
    )
    y = wrapped_text(c, decl, m, y, rw, size=8.5, leading=12)
    y -= 25

    # Signatures
    sig_x = m
    hline(c, sig_x, sig_x + 220, y, 1)
    hline(c, sig_x + 260, W - m, y, 1)
    y -= 12
    c.setFont('Helvetica', 8)
    c.drawString(sig_x, y, 'Signature of Petitioner (Pro Se)')
    c.drawString(sig_x + 260, y, f'Date: {TODAY_SHORT}')
    y -= 16
    c.setFont('Helvetica', 8.5)
    c.drawString(sig_x, y, DEBTOR['name'] + ' (Pro Se)')
    y -= 11
    c.drawString(sig_x, y, DEBTOR['address'])
    y -= 11
    c.drawString(sig_x, y, DEBTOR['city_state'])

    # Footer
    c.setFont('Helvetica', 7)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(W/2, 0.45 * inch,
        f'Petition for Contested Case Hearing | Case {DEBTOR["case_no"]} | Generated {TODAY} | FormGuide — Precedent Systems')
    c.setFillColor(colors.black)

    c.save()
    print(f'✅ Saved: {output_path}')
    return output_path

if __name__ == '__main__':
    out = build(OUTPUT)
    import shutil
    os.makedirs(FILE_NEXT, exist_ok=True)
    dest = os.path.join(FILE_NEXT, os.path.basename(out))
    shutil.copy(out, dest)
    print(f'📋 Copied to File_Next: {dest}')
