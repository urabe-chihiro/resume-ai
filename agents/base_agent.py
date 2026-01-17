"""Base agent class."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain.llms.base import BaseLLM
from langchain_openai import ChatOpenAI


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, llm: BaseLLM = None, temperature: float = 0.7):
        """Initialize base agent.
        
        Args:
            llm: Language model to use
            temperature: Temperature for generation
        """
        self.llm = llm or ChatOpenAI(temperature=temperature, model="gpt-4")
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Output data from the agent
        """
        pass
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with variables.
        
        Args:
            template: Prompt template
            **kwargs: Variables to fill in template
            
        Returns:
            Formatted prompt
        """
        return template.format(**kwargs)
