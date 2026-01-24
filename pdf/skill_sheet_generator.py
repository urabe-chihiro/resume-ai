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
            fontSize=8,
            textColor=self.COLOR_TEXT,
            spaceAfter=20,
            leading=12,
            alignment=TA_RIGHT,  # Right align
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
            spaceAfter=8,
            spaceBefore=0,
            leading=14,
            alignment=TA_LEFT,
        )
    
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
    
    def _build_story(self, data: Dict[str, Any]) -> List:
        """Build PDF story elements using template-like layout.
        
        Args:
            data: Parsed data
            
        Returns:
            List of story elements
        """
        story = []
        
        # 1. 基本情報 (個人情報) - タイトルなし
        # Header with name and job title
        name_text = data.get('name') or 'Your Name'
        job_title = data.get('job_title') or data.get('role') or ''
        
        # Name (same font size as section header - style_section_header)
        story.append(Paragraph(f"<b>{name_text}</b>", self.style_section_header))
        
        # Job title, residence, years of experience (same font size as regular text)
        contact_parts = []
        if job_title:
            contact_parts.append(job_title)
        if data.get('residence'):
            contact_parts.append(data['residence'] + '在中')
        if data.get('years_of_experience'):
            contact_parts.append(f"経験年数: {data['years_of_experience']}年")
        
        if contact_parts:
            contact_text = ' | '.join(contact_parts)
            story.append(Paragraph(contact_text, self.style_subtitle))
        
        story.append(Spacer(1, 12*mm))
        
        # 2. 職務要約 (アピールポイント)
        summary = data.get('summary')
        if summary:
            # Skip section header since summary already contains formatting
            summary_lines = summary.split('\n')
            for line in summary_lines:
                line = line.strip()
                if line:
                    # Keep the line as-is to preserve formatting like ◉ marks
                    story.append(Paragraph(line, self.style_summary))
            story.append(Spacer(1, 12*mm))
        
        # 3. スキルセット
        # Organize skills by category
        skills = data.get('programming_languages', [])
        if skills or data.get('frameworks') or data.get('testing_tools') or data.get('design_tools'):
            story.append(self._create_section_header('スキルセット'))
            
            # Create table for skills
            skill_table_data = []
            
            if data.get('programming_languages'):
                langs = ', '.join(data['programming_languages']) if isinstance(data['programming_languages'], list) else str(data['programming_languages'])
                skill_table_data.append([
                    Paragraph("<b>プログラミング言語</b>", self.style_skill_category),
                    Paragraph(langs, self.style_skill_items),
                ])
            
            if data.get('frameworks'):
                fws = ', '.join(data['frameworks']) if isinstance(data['frameworks'], list) else str(data['frameworks'])
                skill_table_data.append([
                    Paragraph("<b>フレームワーク</b>", self.style_skill_category),
                    Paragraph(fws, self.style_skill_items),
                ])
            
            if data.get('testing_tools'):
                tools = ', '.join(data['testing_tools']) if isinstance(data['testing_tools'], list) else str(data['testing_tools'])
                skill_table_data.append([
                    Paragraph("<b>テストツール</b>", self.style_skill_category),
                    Paragraph(tools, self.style_skill_items),
                ])
            
            if data.get('design_tools'):
                design = ', '.join(data['design_tools']) if isinstance(data['design_tools'], list) else str(data['design_tools'])
                skill_table_data.append([
                    Paragraph("<b>デザインツール</b>", self.style_skill_category),
                    Paragraph(design, self.style_skill_items),
                ])
            
            if skill_table_data:
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
                story.append(Spacer(1, 12*mm))
        
        # 4. 個人開発 (Personal Projects)
        personal_projects = data.get('personal_projects', [])
        if personal_projects:
            story.append(self._create_section_header('個人開発'))
            
            for project in personal_projects:
                if isinstance(project, dict):
                    title = project.get('title', '')
                    description = project.get('description', '')
                    technologies = project.get('technologies', [])
                    url = project.get('url', '')
                    
                    # Project title
                    if title:
                        story.append(Paragraph(f"<b>{title}</b>", self.style_job_title))
                    
                    # Description
                    if description:
                        story.append(Paragraph(description, self.style_job_detail))
                    
                    # Technologies
                    if technologies:
                        tech_text = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
                        story.append(Paragraph(f"<b>技術:</b> {tech_text}", self.style_job_detail))
                    
                    # URL
                    if url:
                        story.append(Paragraph(f"<b>URL:</b> {url}", self.style_job_detail))
                    
                    story.append(Spacer(1, 8*mm))
        
        # 5. 職務経歴
        work_experiences = data.get('work_experiences', [])
        if work_experiences:
            story.append(self._create_section_header('職務経歴'))
            
            for exp in work_experiences:
                if isinstance(exp, dict):
                    company_name = exp.get('company_name', '')
                    position = exp.get('position', '')
                    period = exp.get('period', '')
                    description = exp.get('description', '')
                    
                    # Company and position
                    if company_name:
                        company_text = f"{company_name} — {position}" if position else company_name
                        story.append(Paragraph(f"<b>{company_text}</b>", self.style_job_title))
                    
                    # Period
                    if period:
                        story.append(Paragraph(f"<i>{period}</i>", self.style_job_detail))
                    
                    # Description
                    if description:
                        story.append(Paragraph(description, self.style_job_detail))
                    
                    story.append(Spacer(1, 8*mm))
        
        return story
    
    def _organize_skills(self, skills: List) -> Dict[str, List[str]]:
        """Organize skills by category.
        
        Args:
            skills: List of skill entries (can be strings or dicts)
            
        Returns:
            Dictionary with skill categories and items
        """
        organized = {}
        
        if not skills:
            return organized
        
        # If skills is a list of simple strings, categorize them
        if all(isinstance(s, str) for s in skills):
            # Check if we can categorize based on content
            organized['スキル'] = skills
            return organized
        
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
            elif isinstance(skill_entry, str):
                if ':' in skill_entry:
                    parts = skill_entry.split(':', 1)
                    category = parts[0].strip()
                    items = [s.strip() for s in parts[1].split(',')]
                    organized[category] = items
                else:
                    # Fallback category
                    if 'スキル' not in organized:
                        organized['スキル'] = []
                    organized['スキル'].append(skill_entry)
        
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
