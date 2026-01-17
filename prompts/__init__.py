"""Prompt templates for agents."""

from .company_analysis import COMPANY_ANALYSIS_PROMPT
from .requirements_extraction import REQUIREMENTS_EXTRACTION_PROMPT
from .resume_structure import RESUME_STRUCTURE_PROMPT
from .resume_generation import RESUME_GENERATION_PROMPT
from .feedback_improvement import FEEDBACK_IMPROVEMENT_PROMPT

__all__ = [
    "COMPANY_ANALYSIS_PROMPT",
    "REQUIREMENTS_EXTRACTION_PROMPT",
    "RESUME_STRUCTURE_PROMPT",
    "RESUME_GENERATION_PROMPT",
    "FEEDBACK_IMPROVEMENT_PROMPT",
]
