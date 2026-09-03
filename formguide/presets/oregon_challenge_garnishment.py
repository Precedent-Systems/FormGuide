#!/usr/bin/env python3
"""
Generate a filled Oregon Challenge to Garnishment (ORS 18.700)
using the FormGuide filling engine, pre-populated from Annika's profile.
Features:
- Correct July 1, 2026 statutory weekly wage floor of $400/wk ($800 biweekly) under ORS 18.385
- Correct vehicle equity exemption (pickup truck) under ORS 18.345(1)(d)
- OregonSaves Retirement Account Exemption under ORS 18.358 / ORS 178.200 et seq.
- Homestead exemption and judgment lien defense under ORS 18.395 ($158,300 limit)
- Exempt wage tracing for bank accounts under ORS 18.385 / ORS 411.760
- Dynamic date updating on every run
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
    'address':    'P.O. Box 1108 (ACP 0030-24) / 12054 Chapin Ct.',
    'city_state': 'Oregon City, OR 97045',
    'phone':      '(971) 359-8578',
    'email':      'erikssona@icloud.com',
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
EXEMPTIONS = [
    ('1', 'WAGE EXEMPTION — ORS 18.375 / ORS 18.385',
     'Debtor claims statutory exemption of all disposable earnings. Debtor earns $21.25/hr working ~32 hours per 2-week pay period '
     '($680.00 gross / ~$533.82 net after taxes, SEIU union dues, and OregonSaves contributions). Under ORS 18.385 '
     '(effective July 1, 2026), the exempt minimum floor is $400.00 per workweek ($800.00 biweekly). Because Debtor\'s disposable '
     'earnings ($533.82 biweekly) fall entirely below the $800.00 statutory floor, 100% of Debtor\'s earnings are exempt ($0.00 garnishable).'),

    ('13', 'VEHICLE EXEMPTION (PICKUP TRUCK) — ORS 18.345(1)(d)',
     'Debtor claims exemption for one motor vehicle (pickup truck) under ORS 18.345(1)(d). The vehicle has extensive cosmetic damage, '
     'expired registration, and salvage status, with an estimated fair market value of approximately $500–$1,000 and zero outstanding loans, '
     'resulting in equity well below the $10,000 statutory limit.'),

    ('17', 'RETIREMENT PLAN / OREGONSAVES IRA — ORS 18.358 / ORS 178.200 et seq.',
     'Debtor claims statutory exemption for Debtor\'s state-administered OregonSaves Roth IRA retirement plan account (current balance < $100.00). '
     'Under ORS 18.358 and ORS 178.200 et seq., all funds, payroll withholding contributions, and beneficial interests in qualified retirement '
     'plans and state auto-IRAs are 100% exempt from execution and garnishment.'),

    ('12', 'HOUSEHOLD GOODS — ORS 18.345(1)(b)',
     'Debtor claims exemption for household goods, furniture, and personal items with combined value not exceeding the $3,000 limit.'),

    ('2', 'HOMESTEAD EXEMPTION & JUDGMENT LIEN DEFENSE — ORS 18.395',
     'Debtor asserts the Oregon Homestead Exemption for debtor\'s primary residence and actual abode located at 12054 Chapin Court, '
     'Oregon City, OR 97045. Under ORS 18.395, debtor\'s homestead is exempt from judgment liens and execution up to $158,300.00. '
     'To the extent garnishor recorded a judgment lien in Clackamas County, that lien attaches only to value exceeding $158,300; '
     'because no excess equity exists over senior encumbrances and the statutory exemption, the lien cannot attach or support execution.'),

    ('27', 'EXEMPT FUNDS IN BANK ACCOUNTS — ORS 18.385 / ORS 411.760',
     'To the extent any funds in debtor\'s financial institution account represent exempt wages or public benefits, '
     'said funds remain fully exempt from execution pursuant to ORS 18.385 and ORS 411.760.'),
]

TODAY = datetime.date.today().strftime('%B %d, %Y')
TODAY_SHORT = datetime.date.today().strftime('%m/%d/%Y')

# ── Drawing helpers ──────────────────────────────────────────────────────────
def hline(c, x1, x2, y, width=0.5, color=colors.black):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)

def label_field(c, label, value, x, y, label_width=120, font_size=8):
    c.setFont('Helvetica-Bold', font_size)
    c.drawString(x, y, label)
    c.setFont('Helvetica', font_size)
    c.drawString(x + label_width, y, value)

def wrapped_text(c, text, x, y, max_width, font='Helvetica', size=7.5, leading=9.2):
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
    m = 0.6 * inch   # margin
    rw = W - 2 * m   # usable width

    # ── PAGE 1 ────────────────────────────────────────────────────────────────
    y = H - 0.45 * inch

    # Header
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(W/2, y, CASE['court'].upper())
    y -= 12
    hline(c, m, W-m, y, 1.2)
    y -= 14

    # Caption
    c.setFont('Helvetica', 8.5)
    c.drawString(m, y, CASE['creditor'] + ',')
    c.setFont('Helvetica-Bold', 8)
    c.drawRightString(W-m, y, 'CHALLENGE TO GARNISHMENT')
    y -= 11
    c.setFont('Helvetica', 8.5)
    c.drawString(m + 15, y, 'Plaintiff,')
    c.setFont('Helvetica-Bold', 8)
    c.drawRightString(W-m, y, f'Case No. {CASE["case_no"]}')
    y -= 11
    c.setFont('Helvetica', 8.5)
    c.drawString(m, y, 'v.')
    y -= 11
    c.drawString(m, y, DEBTOR['name'] + ',')
    y -= 11
    c.drawString(m + 15, y, 'Defendant / Debtor.')
    y -= 5
    hline(c, m, W-m, y, 1.2)
    y -= 13

    # Intro
    c.setFont('Helvetica-Bold', 9)
    c.drawString(m, y, 'DEBTOR\'S CHALLENGE TO GARNISHMENT AND CLAIM OF EXEMPTIONS')
    y -= 10
    c.setFont('Helvetica-Bold', 8)
    c.drawString(m, y, '(ORS 18.700 — Oregon Challenge to Garnishment)')
    y -= 12

    intro = (
        f'I, {DEBTOR["name"]}, am the Debtor in this matter. Pursuant to ORS 18.700 et seq., '
        'I hereby challenge the garnishment and claim the following statutory property, earnings, and retirement benefits '
        'as exempt from execution under Oregon law.'
    )
    y = wrapped_text(c, intro, m, y, rw, size=8, leading=10)
    y -= 4

    # Debtor info block
    hline(c, m, W-m, y+3, 0.5, colors.HexColor('#888888'))
    y -= 3
    c.setFont('Helvetica-Bold', 8)
    c.drawString(m, y, 'DEBTOR INFORMATION')
    y -= 9
    label_field(c, 'Name:', DEBTOR['name'],     m, y)
    y -= 9
    label_field(c, 'Address:', DEBTOR['address'], m, y)
    y -= 9
    label_field(c, 'Phone / Email:', f"{DEBTOR['phone']}  |  {DEBTOR['email']}", m, y)
    c.setFont('Helvetica-Bold', 8)
    c.drawString(m + 300, y, 'Total Claimed:')
    c.setFont('Helvetica', 8)
    c.drawString(m + 365, y, CASE['total'])
    y -= 6

    # Exemptions
    hline(c, m, W-m, y+3, 0.5, colors.HexColor('#888888'))
    y -= 3
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(m, y, 'CLAIMED EXEMPTIONS')
    y -= 7

    for i, (num, title, body) in enumerate(EXEMPTIONS, 1):
        c.setFont('Helvetica-Bold', 7.8)
        c.drawString(m, y, f'{i}.  Exemption No. {num} — {title}')
        y -= 9
        y = wrapped_text(c, body, m + 12, y, rw - 12, size=7.2, leading=8.8)
        y -= 3

    # Wage calculation table
    hline(c, m, W-m, y+3, 0.5, colors.HexColor('#bbbbbb'))
    y -= 3
    c.setFont('Helvetica-Bold', 8)
    c.drawString(m, y, 'WAGE EXEMPTION CALCULATION (ORS 18.385 — Post-July 1, 2026 Standards)')
    y -= 9

    rows = [
        ('Gross wages ($21.25/hr × 32 hrs / 2-wk period)', '$680.00 biweekly ($340.00/wk)'),
        ('Deductions (Taxes, SEIU Union Dues, OregonSaves Retirement)', '~$146.18 / period'),
        ('Net disposable earnings per pay period',          '~$533.82 biweekly (~$266.91/wk)'),
        ('75% of disposable earnings protection',            '~$400.37 / period'),
        ('Statutory weekly floor exemption ($400/wk floor)', '$400.00/wk ($800.00 biweekly)'),
        ('Exempt amount (greater of 75% or $800 floor)',    'ALL wages exempt ($533.82)'),
        ('Amount subject to garnishment',                 '$0.00 (100% EXEMPT)'),
    ]
    col1 = m + 10
    c.setFont('Helvetica', 7.5)
    for label, val in rows:
        c.drawString(col1, y, label)
        c.drawRightString(W - m, y, val)
        hline(c, col1, W-m, y-1.5, 0.25, colors.HexColor('#dddddd'))
        y -= 8.5
    y -= 3

    # Declaration
    hline(c, m, W-m, y+3, 0.5, colors.HexColor('#888888'))
    y -= 3
    c.setFont('Helvetica-Bold', 8)
    c.drawString(m, y, 'DECLARATION')
    y -= 8
    decl = (
        'I declare under penalty of perjury under the laws of the State of Oregon that the '
        'foregoing is true and correct, and that the property, retirement assets, and earnings identified above are exempt from '
        'garnishment under Oregon law.'
    )
    y = wrapped_text(c, decl, m, y, rw, size=7.2, leading=8.5)
    y -= 10

    # Signature block
    sig_x = m
    hline(c, sig_x, sig_x + 190, y, 1)
    hline(c, sig_x + 230, W - m, y, 1)
    y -= 8
    c.setFont('Helvetica', 7)
    c.drawString(sig_x, y, 'Signature of Debtor (Pro Se)')
    c.drawString(sig_x + 230, y, f'Date: {TODAY_SHORT}')
    y -= 11
    c.setFont('Helvetica', 7.5)
    c.drawString(sig_x, y, DEBTOR['name'] + ' (Pro Se)')
    y -= 8
    c.drawString(sig_x, y, DEBTOR['address'])
    y -= 8
    c.drawString(sig_x, y, f"{DEBTOR['city_state']} | {DEBTOR['phone']}")

    # Footer
    c.setFont('Helvetica', 6.2)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(W/2, 0.3 * inch,
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
    import shutil, os
    os.makedirs(FILE_NEXT, exist_ok=True)
    dest = os.path.join(FILE_NEXT, os.path.basename(out))
    shutil.copy(out, dest)
    print(f'📋 Copied to File_Next: {dest}')
