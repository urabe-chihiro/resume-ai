"""PDF generator from Markdown resume."""

import re
from typing import List, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os


class PDFGenerator:
    """Generate PDF from Markdown resume."""
    
    def __init__(self):
        """Initialize PDF generator."""
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_CENTER,
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#34495e'),
            spaceBefore=12,
            spaceAfter=6,
            borderWidth=1,
            borderColor=HexColor('#3498db'),
            borderPadding=5,
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=HexColor('#2c3e50'),
            spaceBefore=8,
            spaceAfter=4,
            fontName='Helvetica-Bold',
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=6,
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=12,
        ))
    
    def markdown_to_pdf(self, markdown_text: str, output_path: str) -> None:
        """Convert markdown to PDF.
        
        Args:
            markdown_text: Resume in markdown format
            output_path: Path to save PDF file
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
        )
        
        # Parse markdown and create flowables
        story = self._parse_markdown(markdown_text)
        
        # Build PDF
        doc.build(story)
    
    def _parse_markdown(self, markdown_text: str) -> List:
        """Parse markdown text and convert to reportlab flowables.
        
        Args:
            markdown_text: Markdown text
            
        Returns:
            List of reportlab flowables
        """
        story = []
        lines = markdown_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Title (# Title)
            if line.startswith('# '):
                title = line[2:].strip()
                story.append(Paragraph(self._escape_html(title), self.styles['ResumeTitle']))
                story.append(Spacer(1, 6*mm))
            
            # Section heading (## Section)
            elif line.startswith('## '):
                heading = line[3:].strip()
                story.append(Spacer(1, 4*mm))
                story.append(Paragraph(self._escape_html(heading), self.styles['SectionHeading']))
                story.append(Spacer(1, 2*mm))
            
            # Subsection heading (### Subsection)
            elif line.startswith('### '):
                subheading = line[4:].strip()
                story.append(Paragraph(self._escape_html(subheading), self.styles['SubsectionHeading']))
            
            # Horizontal rule
            elif line.startswith('---'):
                story.append(Spacer(1, 2*mm))
            
            # Bullet point
            elif line.startswith('- ') or line.startswith('* '):
                bullet_text = line[2:].strip()
                story.append(Paragraph(f"• {self._escape_html(bullet_text)}", self.styles['ResumeBody']))
            
            # Numbered list
            elif re.match(r'^\d+\.\s', line):
                list_text = re.sub(r'^\d+\.\s', '', line)
                story.append(Paragraph(self._escape_html(list_text), self.styles['ResumeBody']))
            
            # Contact info (if contains @ symbol or starts with specific patterns)
            elif '@' in line or line.startswith('Email:') or line.startswith('Tel:'):
                story.append(Paragraph(self._escape_html(line), self.styles['ContactInfo']))
            
            # Regular paragraph
            else:
                # Handle bold and italic
                formatted_line = self._format_inline_markdown(line)
                story.append(Paragraph(formatted_line, self.styles['ResumeBody']))
            
            i += 1
        
        return story
    
    def _format_inline_markdown(self, text: str) -> str:
        """Format inline markdown (bold, italic).
        
        Args:
            text: Text with markdown formatting
            
        Returns:
            Text with HTML formatting
        """
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        
        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
        # Code: `code`
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
        
        return self._escape_html(text)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters but preserve tags.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Don't escape if it already contains HTML tags we added
        if '<b>' in text or '<i>' in text or '<font' in text:
            return text
        
        # Escape special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        return text
