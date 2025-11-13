from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re
from io import BytesIO

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Create custom styles for resume"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor='#2C3E50',
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor='#34495E',
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor='#2C3E50',
            spaceAfter=4,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor='#000000',
            spaceAfter=4,
            leading=14,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor='#000000',
            leftIndent=20,
            spaceAfter=4,
            leading=14,
            fontName='Helvetica'
        ))
    
    def parse_markdown_to_elements(self, text):
        """Convert markdown-formatted resume to PDF elements"""
        elements = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            if line.startswith('## '):
                header_text = line.replace('## ', '').strip()
                elements.append(Spacer(1, 0.15*inch))
                elements.append(Paragraph(header_text, self.styles['SectionHeader']))
                elements.append(Spacer(1, 0.05*inch))
            
            elif line.startswith('### ') or (line.startswith('**') and line.endswith('**')):
                if line.startswith('### '):
                    header_text = line.replace('### ', '').strip()
                else:
                    header_text = line.replace('**', '').strip()
                elements.append(Paragraph(header_text, self.styles['SubsectionHeader']))
            
            elif line.startswith('- ') or line.startswith('* '):
                bullet_text = line[2:].strip()
                bullet_text = bullet_text.replace('**', '')
                elements.append(Paragraph(f"• {bullet_text}", self.styles['BulletPoint']))
            
            else:
                clean_text = line.replace('**', '')
                if clean_text:
                    elements.append(Paragraph(clean_text, self.styles['CustomBody']))
            
            i += 1
        
        return elements
    
    def create_pdf(self, resume_text, output_filename="customized_resume.pdf"):
        """Generate PDF from resume text"""
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        elements = self.parse_markdown_to_elements(resume_text)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def generate_resume_pdf(self, customized_resume_text):
        """Main method to generate PDF from customized resume"""
        return self.create_pdf(customized_resume_text)