"""
Prompt models for the task assignment system
"""

from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class PromptParameterType(str, Enum):
    """Types of prompt parameters that can be adjusted"""
    CLARITY = "Clarity"  # Vague → Precise
    TONE = "Tone"  # Directive → Empowering
    AGENCY = "Agency"  # Freedom → Strict direction
    EMPATHY = "Empathy"  # None → High


class PromptParameter(BaseModel):
    """Individual parameter for prompt quality"""
    Name: PromptParameterType
    Value: int
    

class Prompt(BaseModel):
    """Prompt model for task assignment"""
    Text: str
    Parameters: List[PromptParameter] = []
    
    def get_parameter_value(self, param_name: str) -> int:
        """Get the value of a specific parameter"""
        for param in self.Parameters:
            if param.Name.value.lower() == param_name.lower():
                return param.Value
        return 5  # Default middle value
    
    def get_average_parameter_value(self) -> float:
        """Calculate average of all parameter values"""
        if not self.Parameters:
            return 5.0  # Default middle value
        return sum(param.Value for param in self.Parameters) / len(self.Parameters)
