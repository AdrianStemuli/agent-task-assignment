"""
Agent models for the task assignment system
"""

from __future__ import annotations
from pydantic import BaseModel
from typing import List, Union
from enum import Enum


class Department(str, Enum):
    """Department enumeration"""
    RESEARCH = "Research"
    MARKETING = "Marketing"
    ENGINEERING = "Engineering"
    HR = "HR"
    SALES = "Sales"
    DESIGN = "Design"
    OPERATIONS = "Operations"


class AgentStat(BaseModel):
    """Individual stat for an agent"""
    Name: str
    StatValueObj: Union[int, float]  # Support both int and float for TokenMultiplier
    
    class Config:
        schema_extra = {
            "example": {
                "Name": "Expertise",
                "StatValueObj": 8
            }
        }


class Agent(BaseModel):
    """Agent model representing an employee in the company"""
    ID: str  # UUID from Unity
    Name: str
    Stats: List[AgentStat]
    
    # Optional fields for backward compatibility and additional features
    Department: Department = Department.RESEARCH
    preferred_tone: str = "balanced"
    autonomy_preference: int = 5
    
    def get_stat_value(self, stat_name: str) -> Union[int, float]:
        """Get the value of a specific stat"""
        for stat in self.Stats:
            if stat.Name.lower() == stat_name.lower():
                return stat.StatValueObj
        return 0
    
    def get_token_multiplier(self) -> float:
        """Get the token multiplier stat"""
        return float(self.get_stat_value("TokenMultiplier") or 1.0)
    
    def get_overall_skill_level(self) -> float:
        """Calculate overall skill level as average of core stats (excluding TokenMultiplier)"""
        if not self.Stats:
            return 0.0
        
        # Exclude TokenMultiplier from skill calculation
        core_stats = [stat for stat in self.Stats if stat.Name.lower() != "tokenmultiplier"]
        if not core_stats:
            return 0.0
            
        return sum(float(stat.StatValueObj) for stat in core_stats) / len(core_stats)
