"""Professional Skill Sheet PDF Generator - Japanese version."""

from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors


class SkillSheetGenerator:
    """Generate professional Japanese skill sheet PDF matching template design."""
    
    # Color scheme - simple and professional
    COLOR_SECTION_HEADER = HexColor('#333333')  # Dark gray for headers
    COLOR_TEXT = HexColor('#666666')  # Black text
    COLOR_LIGHT_TEXT = HexColor('#666666')  # Medium gray text
    COLOR_DIVIDER = HexColor('#cccccc')  # Light gray divider
    
    def __init__(self):
        """Initialize skill sheet generator."""
        self._register_fonts()
        self._create_custom_styles()
    
    def _register_fonts(self):
        """Register Japanese fonts."""
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
            self.font_main = 'HeiseiKakuGo-W5'
            self.font_regular = 'HeiseiMin-W3'
        except Exception:
            self.font_main = 'Helvetica-Bold'
            self.font_regular = 'Helvetica'
    
    def _create_custom_styles(self):
        """Setup custom paragraph styles."""
        # Name/Title
        self.style_name = ParagraphStyle(
            name='NameStyle',
            fontName=self.font_main,
            fontSize=24,
            textColor=self.COLOR_TEXT,
            spaceAfter=4,
            leading=28,
        )
        
        # Subtitle/Role
        self.style_subtitle = ParagraphStyle(
            name='SubtitleStyle',
            fontName=self.font_main,
            fontSize=10,
            textColor=self.COLOR_LIGHT_TEXT,
            spaceAfter=20,
            leading=12,
        )
        
        # Section header
        self.style_section_header = ParagraphStyle(
            name='SectionHeaderStyle',
            fontName=self.font_main,
            fontSize=13,
            textColor=self.COLOR_TEXT,
            spaceBefore=14,
            spaceAfter=14,
            leading=14,
        )
        
        # Skill category
        self.style_skill_category = ParagraphStyle(
            name='SkillCategoryStyle',
            fontName=self.font_main,
            fontSize=8,
            textColor=self.COLOR_LIGHT_TEXT,
            spaceAfter=2,
            leading=10,
        )
        
        # Skill items
        self.style_skill_items = ParagraphStyle(
            name='SkillItemsStyle',
            fontName=self.font_main,
            fontSize=8,
            textColor=self.COLOR_LIGHT_TEXT,
            spaceAfter=6,
            leading=10,
        )
        
        # Job title
        self.style_job_title = ParagraphStyle(
            name='JobTitleStyle',
            fontName=self.font_main,
            fontSize=10,
            textColor=self.COLOR_TEXT,
            spaceAfter=2,
            leading=12,
        )
        
        # Job detail
        self.style_job_detail = ParagraphStyle(
            name='JobDetailStyle',
            fontName=self.font_main,
            fontSize=9,
            textColor=self.COLOR_LIGHT_TEXT,
            spaceAfter=8,
            leading=11,
        )
        
        # Summary
        self.style_summary = ParagraphStyle(
            name='SummaryStyle',
            fontName=self.font_main,
            fontSize=9,
            textColor=self.COLOR_TEXT,
            spaceAfter=6,
            leading=11,
            alignment=TA_JUSTIFY,
        )
    
    def markdown_to_pdf(self, markdown_text: str, output_path: str) -> None:
        """Convert markdown to professional skill sheet PDF.
        
        Args:
            markdown_text: Resume in markdown format
            output_path: Path to save PDF
        """
        # Parse markdown
        data = self._parse_markdown(markdown_text)
        self._generate_pdf(data, output_path)
    
    def data_to_pdf(self, data: Dict[str, Any], output_path: str) -> None:
        """Generate PDF from structured data.
        
        Args:
            data: Structured resume data dictionary
            output_path: Path to save PDF
        """
        self._generate_pdf(data, output_path)
    
    def _generate_pdf(self, data: Dict[str, Any], output_path: str) -> None:
        """Generate PDF from data.
        
        Args:
            data: Parsed/structured data
            output_path: Path to save PDF
        """
    def _generate_pdf(self, data: Dict[str, Any], output_path: str) -> None:
        """Generate PDF from data.
        
        Args:
            data: Parsed/structured data
            output_path: Path to save PDF
        """
        # Create PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=12*mm,
            leftMargin=12*mm,
            topMargin=12*mm,
            bottomMargin=12*mm,
        )
        
        # Build story
        story = self._build_story(data)
        doc.build(story)
    
    def _parse_markdown(self, markdown_text: str) -> Dict[str, Any]:
        """Parse markdown content.
        
        Args:
            markdown_text: Markdown text
            
        Returns:
            Dictionary with parsed data
        """
        # Extract from code block if present
        if '```' in markdown_text:
            parts = markdown_text.split('```')
            if len(parts) >= 3:
                markdown_text = parts[1]
        
        lines = markdown_text.split('\n')
        
        # Initialize data
        data = {
            'name': None,
            'role': None,
            'email': None,
            'phone': None,
            'summary': None,
            'skills': [],
            'experiences': [],
            'education': [],
        }
        
        current_section = None
        current_company = None
        current_company_data = {}
        
        for line in lines:
            stripped = line.strip()
            
            # Main title (name)
            if stripped.startswith('# ') and data['name'] is None:
                data['name'] = stripped[2:].strip()
            
            # Section headers
            elif stripped.startswith('## '):
                section = stripped[3:].strip()
                
                # Save current experience
                if current_company and current_company_data:
                    data['experiences'].append(current_company_data)
                    current_company = None
                    current_company_data = {}
                
                if '職務要約' in section or '要約' in section or 'プロフィール' in section:
                    current_section = 'summary'
                elif 'スキル' in section or '技術スキル' in section:
                    current_section = 'skills'
                elif '職務経歴' in section or '経歴' in section or '経験' in section:
                    current_section = 'experiences'
                else:
                    current_section = None
            
            # Role
            elif stripped.startswith('役職:') or stripped.startswith('職種:'):
                if ':' in stripped:
                    data['role'] = stripped.split(':', 1)[1].strip()
            
            # Company header - both ### and company name format
            elif stripped.startswith('### '):
                if current_company and current_company_data:
                    data['experiences'].append(current_company_data)
                
                current_company = stripped[4:].strip()
                current_company_data = {
                    'company': current_company,
                    'period': None,
                    'position': None,
                    'details': []
                }
                current_section = 'experiences'
            
            # Handle "Company - Position" format in experiences section
            elif current_section == 'experiences' and stripped and ' - ' in stripped and not stripped.startswith('#'):
                # Save previous company if exists
                if current_company and current_company_data:
                    data['experiences'].append(current_company_data)
                
                parts = stripped.split(' - ', 1)
                current_company = parts[0].strip()
                position = parts[1].strip() if len(parts) > 1 else None
                current_company_data = {
                    'company': current_company,
                    'period': None,
                    'position': position,
                    'details': []
                }
            
            # Content based on section
            elif current_section == 'summary' and stripped and not stripped.startswith('#'):
                if data['summary']:
                    data['summary'] += ' ' + stripped
                else:
                    data['summary'] = stripped
            
            elif current_section == 'skills' and stripped:
                if stripped.startswith('- '):
                    skill_line = stripped[2:].strip()
                    # Remove markdown bold markers
                    skill_line = skill_line.replace('**', '')
                    data['skills'].append(skill_line)
                elif ':' in stripped and not stripped.startswith('##'):
                    # Remove markdown bold markers
                    skill_entry = stripped.replace('**', '')
                    data['skills'].append(skill_entry)
            
            elif current_section == 'experiences' and stripped and not stripped.startswith('#'):
                # Only process if we have a current company
                if current_company:
                    if stripped.startswith('期間:') or '〜' in stripped or '年' in stripped:
                        # Remove markdown bold markers
                        period = stripped.replace('**', '')
                        current_company_data['period'] = period
                    elif stripped.startswith('職務:') or stripped.startswith('職位:'):
                        if ':' in stripped:
                            current_company_data['position'] = stripped.split(':', 1)[1].strip()
                    elif stripped.startswith('- ') or stripped.startswith('• '):
                        # Remove markdown bold markers
                        detail = stripped[2:].strip().replace('**', '')
                        current_company_data['details'].append(detail)
                    elif stripped and ' - ' not in stripped:
                        # Remove markdown bold markers
                        detail = stripped.replace('**', '')
                        current_company_data['details'].append(detail)
            
            elif current_section == 'education' and stripped and not stripped.startswith('#'):
                if stripped.startswith('- '):
                    data['education'].append(stripped[2:].strip())
                elif stripped:
                    data['education'].append(stripped)
            
            # Contact info
            elif 'Email:' in stripped or 'email' in stripped.lower():
                if ':' in stripped:
                    data['email'] = stripped.split(':', 1)[1].strip()
            elif any(x in stripped for x in ['Phone:', '電話:', '電話番号:']):
                if ':' in stripped:
                    data['phone'] = stripped.split(':', 1)[1].strip()
        
        # Save last experience
        if current_company and current_company_data:
            data['experiences'].append(current_company_data)
        
        return data
    
    def _build_story(self, data: Dict[str, Any]) -> List:
        """Build PDF story elements using template-like layout.
        
        Args:
            data: Parsed data
            
        Returns:
            List of story elements
        """
        story = []
        
        # Header with name and contact info
        name_text = data['name'] or 'Your Name'
        
        # Create header with name
        story.append(Paragraph(name_text, self.style_name))
        
        # Subtitle/contact info
        subtitle_parts = []
        if data['role']:
            subtitle_parts.append(data['role'])
        if data['email']:
            subtitle_parts.append(data['email'])
        if data['phone']:
            subtitle_parts.append(data['phone'])
        
        if subtitle_parts:
            subtitle_text = ' | '.join(subtitle_parts)
            story.append(Paragraph(subtitle_text, self.style_subtitle))
        
        story.append(Spacer(1, 16*mm))
        
        # Skills section with 2-column table layout
        if data['skills']:
            story.append(self._create_section_header('スキル'))
            
            # Organize skills into columns
            # Handle both structured data format (list of dicts) and markdown format (list of strings)
            skill_items = self._organize_skills(data['skills'])
            
            # Create table data
            skill_table_data = []
            for category, items in skill_items.items():
                # Ensure items is a list of strings
                if isinstance(items, list):
                    skills_text = ', '.join(str(item) for item in items)
                else:
                    skills_text = str(items)
                    
                skill_table_data.append([
                    Paragraph(f"<b>{category}</b>", self.style_skill_category),
                    Paragraph(skills_text, self.style_skill_items),
                ])
            
            # Create skill table
            skill_table = Table(skill_table_data, colWidths=[45*mm, 135*mm])
            skill_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (0, -1), 6),
                ('RIGHTPADDING', (1, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('BORDER', (0, 0), (-1, -1), 0),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.COLOR_DIVIDER),
            ]))
            story.append(skill_table)
            story.append(Spacer(1, 16*mm))
        
        # Summary section
        if data['summary']:
            story.append(self._create_section_header('職務要約'))
            summary_text = ' '.join(data['summary'].split())
            story.append(Paragraph(summary_text, self.style_summary))
            story.append(Spacer(1, 16*mm))
        
        # Professional experience section
        if data['experiences']:
            story.append(self._create_section_header('職務経歴'))
            
            for exp in data['experiences']:
                if exp['company']:
                    # Company and position
                    company_text = exp['company']
                    if exp.get('position'):
                        company_text += f" — {exp['position']}"
                    
                    story.append(Paragraph(company_text, self.style_job_title))
                    
                    # Period
                    if exp.get('period'):
                        story.append(Paragraph(f"期間: {exp['period']}", self.style_job_detail))
                    
                    # Details as bullet points
                    for detail in exp.get('details', []):
                        if detail.strip():
                            story.append(Paragraph(f"• {detail}", self.style_job_detail))
                    
                    story.append(Spacer(1, 6*mm))
        
        return story
    
    def _organize_skills(self, skills: List) -> Dict[str, List[str]]:
        """Organize skills by category.
        
        Args:
            skills: List of skill entries (can be strings or dicts)
            
        Returns:
            Dictionary with skill categories and items
        """
        organized = {}
        
        for skill_entry in skills:
            # Handle structured data format: dict with 'category' and 'items'
            if isinstance(skill_entry, dict):
                category = skill_entry.get('category', 'その他')
                items = skill_entry.get('items', [])
                if isinstance(items, list):
                    organized[category] = items
                else:
                    organized[category] = [items]
            # Handle markdown format: string with category:items format
            elif ':' in skill_entry:
                parts = skill_entry.split(':', 1)
                category = parts[0].strip()
                items = [s.strip() for s in parts[1].split(',')]
                organized[category] = items
            else:
                # Fallback category
                if 'その他' not in organized:
                    organized['その他'] = []
                organized['その他'].append(skill_entry)
        
        return organized
    
    def _create_section_header(self, title: str) -> Table:
        """Create styled section header matching template design.
        
        Args:
            title: Section title
            
        Returns:
            Table element with styled header
        """
        header_table = Table([
            [Paragraph(title, self.style_section_header)]
        ], colWidths=[180*mm])
        
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        return header_table
