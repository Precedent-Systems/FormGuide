#!/usr/bin/env python3
"""
Generate a filled Oregon Challenge to Garnishment (ORS 18.700)
using the FormGuide filling engine, pre-populated from Annika's profile.

Usage:
    python3 generate_challenge_garnishment.py

Output:
    Oregon_Challenge_to_Garnishment_FILLED.pdf
"""

import sys, os, datetime
sys.path.insert(0, '/home/annika/FormGuide')

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUTPUT = os.path.expanduser(
    '~/case-workspace/epa-complaint/deliverables/Oregon_Challenge_to_Garnishment_FILLED.pdf'
)
FILE_NEXT = os.path.expanduser('~/google_drive_intake/File_Next/')

# ── Debtor profile ──────────────────────────────────────────────────────────
DEBTOR = {
    'name':       'Annika U. Eriksson',
    'address':    '12054 Chapin Ct.',
    'city_state': 'Oregon City, OR 97045',
    'phone':      '(503) 555-0199',
}
CASE = {
    'court':      'Circuit Court of Washington County, State of Oregon',
    'case_no':    '21SC17276',
    'creditor':   'Accounts Receivable, Inc., a Washington Corporation',
    'garnishee':  'State of Oregon',
    'total':      '$9,736.46',
    'judgment':   'November 16, 2021',
}

# ── Exemptions being claimed ─────────────────────────────────────────────────
# ORS 18.375/18.385 — 75% of disposable earnings + wage floor
EXEMPTIONS = [
    ('1', 'WAGE EXEMPTION — ORS 18.375 / ORS 18.385',
     'Debtor claims exemption of disposable earnings. Debtor\'s take-home wages are '
     'approximately $533.82 per pay period as a State of Oregon DHS Seniors & People with Disabilities Home Care Worker. Under ORS 18.385, '
     'the exempt amount is the GREATER of (a) 75% of disposable earnings (~$400.37/period) '
     'OR (b) $338.00 per workweek. Debtor\'s total earnings fall at or below the '
     'statutory floor exemption; accordingly, ALL wages are exempt from garnishment.'),

    ('13', 'VEHICLE — ORS 18.345(1)(d)',
     'Debtor claims exemption for one motor vehicle up to $10,000 in equity value. '
     'Vehicle is the only means of transport available and is necessary for employment.'),

    ('12', 'HOUSEHOLD GOODS — ORS 18.345(1)(b)',
     'Debtor claims exemption for household goods, furniture, and utensils '
     'with combined value not exceeding $3,000.'),

    ('27', 'BANK ACCOUNT — ORS 18.785',
     'Debtor claims exemption of up to $2,500 in financial institution accounts '
     'to the extent traceable to exempt wages or public benefits.'),
]

TODAY = datetime.date.today().strftime('%B %d, %Y')
TODAY_SHORT = datetime.date.today().strftime('%m/%d/%Y')

# ── Drawing helpers ──────────────────────────────────────────────────────────
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

# ── Build PDF ────────────────────────────────────────────────────────────────
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
    c.drawCentredString(W/2, y, CASE['court'].upper())
    y -= 16
    hline(c, m, W-m, y, 1.5)
    y -= 18

    # Caption
    c.setFont('Helvetica', 9.5)
    c.drawString(m, y, CASE['creditor'] + ',')
    c.setFont('Helvetica-Bold', 9)
    c.drawRightString(W-m, y, 'CHALLENGE TO GARNISHMENT')
    y -= 13
    c.setFont('Helvetica', 9.5)
    c.drawString(m + 20, y, 'Plaintiff,')
    c.setFont('Helvetica-Bold', 9)
    c.drawRightString(W-m, y, f'Case No. {CASE["case_no"]}')
    y -= 13
    c.setFont('Helvetica', 9.5)
    c.drawString(m, y, 'v.')
    y -= 13
    c.drawString(m, y, DEBTOR['name'] + ',')
    y -= 13
    c.drawString(m + 20, y, 'Defendant / Debtor.')
    y -= 8
    hline(c, m, W-m, y, 1.5)
    y -= 20

    # Intro
    c.setFont('Helvetica-Bold', 10)
    c.drawString(m, y, 'DEBTOR\'S CHALLENGE TO GARNISHMENT AND CLAIM OF EXEMPTIONS')
    y -= 14
    c.setFont('Helvetica-Bold', 9)
    c.drawString(m, y, '(ORS 18.700 — Oregon Challenge to Garnishment)')
    y -= 18

    intro = (
        f'I, {DEBTOR["name"]}, am the Debtor in this matter. I have received the Writ of '
        f'Garnishment issued in Case No. {CASE["case_no"]}. Pursuant to ORS 18.700 et seq., '
        'I hereby challenge the garnishment and claim the following property as exempt from '
        'execution under Oregon law.'
    )
    y = wrapped_text(c, intro, m, y, rw, size=9, leading=13)
    y -= 16

    # Debtor info block
    hline(c, m, W-m, y+4, 0.5, colors.HexColor('#888888'))
    y -= 4
    c.setFont('Helvetica-Bold', 9)
    c.drawString(m, y, 'DEBTOR INFORMATION')
    y -= 13
    label_field(c, 'Name:', DEBTOR['name'],     m, y)
    y -= 12
    label_field(c, 'Address:', DEBTOR['address'], m, y)
    y -= 12
    label_field(c, '', DEBTOR['city_state'], m, y)
    y -= 12
    label_field(c, 'Phone:', DEBTOR['phone'], m, y)
    y -= 12
    label_field(c, 'Garnishment Total Claimed:', CASE['total'], m, y)
    y -= 20

    # Exemptions
    hline(c, m, W-m, y+4, 0.5, colors.HexColor('#888888'))
    y -= 4
    c.setFont('Helvetica-Bold', 10)
    c.drawString(m, y, 'CLAIMED EXEMPTIONS')
    y -= 16

    for i, (num, title, body) in enumerate(EXEMPTIONS, 1):
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(m, y, f'{i}.  Exemption No. {num} — {title}')
        y -= 13
        y = wrapped_text(c, body, m + 16, y, rw - 16, size=8.5, leading=12)
        y -= 12

    # Wage calculation table
    hline(c, m, W-m, y+4, 0.5, colors.HexColor('#bbbbbb'))
    y -= 8
    c.setFont('Helvetica-Bold', 9)
    c.drawString(m, y, 'WAGE EXEMPTION CALCULATION (ORS 18.385)')
    y -= 13

    rows = [
        ('Gross wages per pay period',         '$533.82'),
        ('Estimated take-home (disposable)',    '~$533.82'),
        ('75% of disposable earnings',         '~$400.37'),
        ('Statutory weekly floor (current)',   '$338.00/week'),
        ('Exempt amount (greater of above)',   'ALL wages exempt'),
        ('Amount subject to garnishment',      '$0.00'),
    ]
    col1 = m + 10
    col2 = W - m - 120
    c.setFont('Helvetica', 8.5)
    for label, val in rows:
        c.drawString(col1, y, label)
        c.drawRightString(W - m, y, val)
        hline(c, col1, W-m, y-2, 0.25, colors.HexColor('#dddddd'))
        y -= 12
    y -= 10

    # Declaration
    hline(c, m, W-m, y+4, 0.5, colors.HexColor('#888888'))
    y -= 8
    c.setFont('Helvetica-Bold', 9)
    c.drawString(m, y, 'DECLARATION')
    y -= 13
    decl = (
        'I declare under penalty of perjury under the laws of the State of Oregon that the '
        'foregoing is true and correct, and that the property identified above is exempt from '
        'garnishment under Oregon law.'
    )
    y = wrapped_text(c, decl, m, y, rw, size=8.5, leading=12)
    y -= 28

    # Signature block
    sig_x = m
    hline(c, sig_x, sig_x + 220, y, 1)
    hline(c, sig_x + 260, W - m, y, 1)
    y -= 12
    c.setFont('Helvetica', 8)
    c.drawString(sig_x, y, 'Signature of Debtor (Pro Se)')
    c.drawString(sig_x + 260, y, f'Date: {TODAY_SHORT}')
    y -= 16
    c.setFont('Helvetica', 8.5)
    c.drawString(sig_x, y, DEBTOR['name'] + ' (Pro Se)')
    y -= 11
    c.drawString(sig_x, y, DEBTOR['address'])
    y -= 11
    c.drawString(sig_x, y, DEBTOR['city_state'])
    y -= 11
    c.drawString(sig_x, y, DEBTOR['phone'])

    # Footer
    c.setFont('Helvetica', 7)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(W/2, 0.45 * inch,
        f'Challenge to Garnishment | Case {CASE["case_no"]} | Generated {TODAY} | FormGuide — Precedent Systems')
    c.setFillColor(colors.black)

    # ── PAGE 2 — Certificate of Service ───────────────────────────────────────
    c.showPage()
    y = H - 0.6 * inch

    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(W/2, y, CASE['court'].upper())
    y -= 16
    hline(c, m, W-m, y, 1.5)
    y -= 22

    c.setFont('Helvetica-Bold', 9.5)
    c.drawString(m, y, f'{CASE["creditor"]}, Plaintiff  v.  {DEBTOR["name"]}, Defendant')
    c.drawRightString(W-m, y, f'Case No. {CASE["case_no"]}')
    y -= 22

    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(W/2, y, 'CERTIFICATE OF SERVICE')
    y -= 20

    cert = (
        f'I, {DEBTOR["name"]}, hereby certify that on {TODAY}, I served a true copy of the '
        'foregoing Challenge to Garnishment and Claim of Exemptions by first-class U.S. Mail, '
        'postage prepaid, addressed to:'
    )
    y = wrapped_text(c, cert, m, y, rw, size=9, leading=13)
    y -= 18

    # Service addresses
    addrs = [
        ('Court Administrator', [
            'Washington County Circuit Court',
            '150 N 1st Avenue',
            'Hillsboro, OR 97124',
        ]),
        ('Garnishor / Attorney for Creditor', [
            'Justin Murphy, OSB #195532',
            'Accounts Receivable, Inc.',
            '4001 Main Street, Suite 50',
            'Vancouver, WA 98663',
        ]),
    ]
    for title, lines in addrs:
        c.setFont('Helvetica-Bold', 9)
        c.drawString(m + 20, y, title + ':')
        y -= 12
        c.setFont('Helvetica', 9)
        for ln in lines:
            c.drawString(m + 40, y, ln)
            y -= 12
        y -= 6

    y -= 20
    hline(c, m, m + 220, y, 1)
    y -= 12
    c.setFont('Helvetica', 8.5)
    c.drawString(m, y, DEBTOR['name'] + ' (Pro Se Debtor)')
    y -= 11
    c.drawString(m, y, f'Date: {TODAY_SHORT}')

    c.setFont('Helvetica', 7)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(W/2, 0.45 * inch,
        f'Certificate of Service | Case {CASE["case_no"]} | Generated {TODAY} | FormGuide — Precedent Systems')

    c.save()
    print(f'✅ Saved: {output_path}')
    return output_path

if __name__ == '__main__':
    out = build(OUTPUT)
    # Copy to File_Next for sync
    import shutil, os
    os.makedirs(FILE_NEXT, exist_ok=True)
    dest = os.path.join(FILE_NEXT, os.path.basename(out))
    shutil.copy(out, dest)
    print(f'📋 Copied to File_Next: {dest}')
