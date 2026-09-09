from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'uploads' / 'evidence'


def build_report(path, title, subtitle, summary, rows):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('Kicker', parent=styles['BodyText'], textColor=colors.HexColor('#0A4F8F'), fontName='Helvetica-Bold', fontSize=8, leading=11, spaceAfter=4))
    styles.add(ParagraphStyle('DocumentTitle', parent=styles['Title'], textColor=colors.HexColor('#062B52'), fontName='Helvetica-Bold', fontSize=18, leading=23, spaceAfter=6))
    styles.add(ParagraphStyle('SubTitle', parent=styles['BodyText'], textColor=colors.HexColor('#496274'), fontSize=9, leading=13, spaceAfter=16))
    styles.add(ParagraphStyle('Section', parent=styles['Heading2'], textColor=colors.HexColor('#0A4F8F'), fontName='Helvetica-Bold', fontSize=12, leading=16, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle('Body', parent=styles['BodyText'], textColor=colors.HexColor('#243B4A'), fontSize=10, leading=15, alignment=TA_LEFT))

    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    flow = [
        Paragraph('GOVERNMENT OF MAHARASHTRA | INNOVATION PROCUREMENT BRIDGE', styles['Kicker']),
        Paragraph(title, styles['DocumentTitle']),
        Paragraph(subtitle, styles['SubTitle']),
        Paragraph('Submission summary', styles['Section']),
        Paragraph(summary, styles['Body']),
        Spacer(1, 12),
    ]
    table = Table([['Verification item', 'Recorded result']] + rows, colWidths=[74 * mm, 98 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#062B52')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEADING', (0, 0), (-1, -1), 13),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4F8FB')),
        ('GRID', (0, 0), (-1, -1), .35, colors.HexColor('#C9D7E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    flow += [table, Spacer(1, 14), Paragraph('Declaration', styles['Section']), Paragraph('This sample evidence document is provided for the SIH 2026 demonstration. Its file fingerprint is suitable for recording in the Procurement Audit Ledger; operational source data remains within the authorised portal.', styles['Body'])]
    doc.build(flow)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_report(
        OUTPUT / 'milestone_1_report.pdf',
        'Phase 1 - Sensor Hardware Deployment',
        'Pilot: IoT Sensor Network for Rural Water Quality Monitoring | Submission reference: M-001',
        'Twenty-five solar-powered monitoring nodes were installed and commissioned across designated pilot villages in the Konkan region. All locations completed connectivity and baseline water-quality tests.',
        [
            ['Deployment coverage', '25 of 25 field nodes installed and reporting'],
            ['Power verification', 'Solar charge controller and battery checks passed at each site'],
            ['Connectivity', 'GSM telemetry confirmed; offline buffering enabled'],
            ['Baseline parameters', 'pH, TDS and turbidity readings captured at commissioning'],
        ],
    )
    build_report(
        OUTPUT / 'dashboard_integration_proof.pdf',
        'Phase 2 - Telemetry Dashboard Integration',
        'Pilot: IoT Sensor Network for Rural Water Quality Monitoring | Submission reference: M-002',
        'The demonstration dashboard received encrypted field telemetry and generated threshold alerts for pilot operators. This proof records representative integration checks for evaluator review.',
        [
            ['Telemetry ingestion', '25 active device streams accepted by the dashboard'],
            ['Alert workflow', 'Contamination threshold test created a notification in 2.3 minutes'],
            ['Access controls', 'Government reviewer and startup operator roles tested'],
            ['Audit readiness', 'Milestone evidence submission can be sealed in the audit ledger'],
        ],
    )


if __name__ == '__main__':
    main()
