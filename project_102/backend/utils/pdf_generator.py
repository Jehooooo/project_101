"""
PDF Generator Utility for DMMMSU-SLUC Disaster Monitoring System
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

def generate_incident_pdf(incident, report_folder):
    """
    Generate PDF report for a single incident
    
    Args:
        incident: Incident model object
        report_folder: Folder path to save the PDF
        
    Returns:
        str: Path to generated PDF file
    """
    # Create filename
    filename = f"incident_{incident.incident_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(report_folder, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        fontName='Helvetica-Bold'
    )
    
    # Header
    elements.append(Paragraph("DMMMSU - South La Union Campus", title_style))
    elements.append(Paragraph("Disaster/Emergency Incident Report", subtitle_style))
    elements.append(Paragraph(f"Report ID: {incident.incident_id}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Horizontal line
    line_data = [['']]
    line_table = Table(line_data, colWidths=[6*inch])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Incident Details Section
    elements.append(Paragraph("INCIDENT DETAILS", header_style))
    
    # Create details table
    details_data = [
        [Paragraph("<b>Date of Incident:</b>", normal_style), 
         Paragraph(incident.date.strftime('%B %d, %Y') if incident.date else 'N/A', normal_style)],
        [Paragraph("<b>Time of Incident:</b>", normal_style), 
         Paragraph(incident.time.strftime('%I:%M %p') if incident.time else 'N/A', normal_style)],
        [Paragraph("<b>Location:</b>", normal_style), 
         Paragraph(incident.location or 'N/A', normal_style)],
        [Paragraph("<b>Cause of Incident:</b>", normal_style), 
         Paragraph(incident.cause or 'N/A', normal_style)],
        [Paragraph("<b>Status:</b>", normal_style), 
         Paragraph(f"<font color='{get_status_color(incident.status)}'>{incident.status}</font>", normal_style)],
        [Paragraph("<b>Reported By:</b>", normal_style), 
         Paragraph(incident.reporter.full_name if incident.reporter else 'N/A', normal_style)],
        [Paragraph("<b>Date Reported:</b>", normal_style), 
         Paragraph(incident.created_at.strftime('%B %d, %Y at %I:%M %p') if incident.created_at else 'N/A', normal_style)],
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Description Section
    elements.append(Paragraph("DESCRIPTION", header_style))
    description_para = Paragraph(
        incident.description.replace('\n', '<br/>') or 'No description provided.',
        normal_style
    )
    elements.append(description_para)
    elements.append(Spacer(1, 0.2*inch))
    
    # Supporting Information Section
    elements.append(Paragraph("SUPPORTING INFORMATION", header_style))
    if incident.supporting_file:
        supporting_text = f"Supporting documents have been attached to this report.\nFile: {os.path.basename(incident.supporting_file)}"
    else:
        supporting_text = "No supporting documents attached."
    elements.append(Paragraph(supporting_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_data = [['']]
    footer_table = Table(footer_data, colWidths=[6*inch])
    footer_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 0.1*inch))
    
    footer_text = f"""
    <para alignment="center" fontSize="8" textColor="#6b7280">
    This report was generated automatically by the DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.<br/>
    Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
    © 2024 DMMMSU - South La Union Campus. All rights reserved.
    </para>
    """
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    return filepath


def generate_full_report_pdf(incidents, report_folder, date_from=None, date_to=None):
    """
    Generate compiled PDF report for multiple incidents
    
    Args:
        incidents: List of Incident model objects
        report_folder: Folder path to save the PDF
        date_from: Start date filter (optional)
        date_to: End date filter (optional)
        
    Returns:
        str: Path to generated PDF file
    """
    # Create filename
    filename = f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(report_folder, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6
    )
    
    # Header
    elements.append(Paragraph("DMMMSU - South La Union Campus", title_style))
    elements.append(Paragraph("Disaster/Emergency Incident Report", subtitle_style))
    elements.append(Paragraph("COMPILED INCIDENT REPORT", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Report period
    if date_from and date_to:
        period_text = f"Report Period: {date_from} to {date_to}"
    elif date_from:
        period_text = f"Report Period: From {date_from}"
    elif date_to:
        period_text = f"Report Period: Until {date_to}"
    else:
        period_text = "Report Period: All Time"
    
    elements.append(Paragraph(period_text, subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Horizontal line
    line_data = [['']]
    line_table = Table(line_data, colWidths=[6*inch])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary Statistics
    elements.append(Paragraph("SUMMARY STATISTICS", header_style))
    
    total = len(incidents)
    pending = sum(1 for i in incidents if i.status == 'Pending')
    in_progress = sum(1 for i in incidents if i.status == 'In Progress')
    solved = sum(1 for i in incidents if i.status == 'Solved')
    
    summary_data = [
        [Paragraph("<b>Total Incidents:</b>", normal_style), 
         Paragraph(str(total), normal_style)],
        [Paragraph("<b>Pending:</b>", normal_style), 
         Paragraph(str(pending), normal_style)],
        [Paragraph("<b>In Progress:</b>", normal_style), 
         Paragraph(str(in_progress), normal_style)],
        [Paragraph("<b>Solved:</b>", normal_style), 
         Paragraph(str(solved), normal_style)],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Incident List
    elements.append(Paragraph("INCIDENT DETAILS", header_style))
    elements.append(Spacer(1, 0.1*inch))
    
    if not incidents:
        elements.append(Paragraph("No incidents found for the selected criteria.", normal_style))
    else:
        for idx, incident in enumerate(incidents, 1):
            # Incident header
            incident_header = f"<b>{idx}. Incident ID: {incident.incident_id}</b>"
            elements.append(Paragraph(incident_header, normal_style))
            
            # Incident details
            incident_data = [
                [Paragraph("<b>Date:</b>", normal_style), 
                 Paragraph(incident.date.strftime('%B %d, %Y') if incident.date else 'N/A', normal_style),
                 Paragraph("<b>Time:</b>", normal_style), 
                 Paragraph(incident.time.strftime('%I:%M %p') if incident.time else 'N/A', normal_style)],
                [Paragraph("<b>Location:</b>", normal_style), 
                 Paragraph(incident.location or 'N/A', normal_style),
                 Paragraph("<b>Status:</b>", normal_style), 
                 Paragraph(f"<font color='{get_status_color(incident.status)}'>{incident.status}</font>", normal_style)],
                [Paragraph("<b>Cause:</b>", normal_style), 
                 Paragraph(incident.cause or 'N/A', normal_style),
                 Paragraph("<b>Reported By:</b>", normal_style), 
                 Paragraph(incident.reporter.full_name if incident.reporter else 'N/A', normal_style)],
            ]
            
            incident_table = Table(incident_data, colWidths=[1*inch, 2*inch, 1*inch, 2*inch])
            incident_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(incident_table)
            
            # Description
            elements.append(Paragraph("<b>Description:</b>", normal_style))
            desc = incident.description.replace('\n', '<br/>')[:200] + "..." if len(incident.description) > 200 else incident.description.replace('\n', '<br/>')
            elements.append(Paragraph(desc or 'No description provided.', normal_style))
            elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_data = [['']]
    footer_table = Table(footer_data, colWidths=[6*inch])
    footer_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 0.1*inch))
    
    footer_text = f"""
    <para alignment="center" fontSize="8" textColor="#6b7280">
    This compiled report was generated by the DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System.<br/>
    Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
    © 2024 DMMMSU - South La Union Campus. All rights reserved.
    </para>
    """
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    return filepath


def get_status_color(status):
    """Get hex color code for status"""
    colors_map = {
        'Pending': '#dc2626',
        'In Progress': '#d97706',
        'Solved': '#059669'
    }
    return colors_map.get(status, '#6b7280')
