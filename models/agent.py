"""
Agent models for the task assignment system
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class Department(str, Enum):
    """Available departments in the company"""
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
    Value: int
    
    class Config:
        schema_extra = {
            "example": {
                "Name": "Expertise",
                "Value": 5
            }
        }


class Agent(BaseModel):
    """Agent model representing an employee in the company"""
    Name: str
    Department: Department
    Stats: List[AgentStat]
    preferred_tone: str = "balanced"
    autonomy_preference: int = 5
    
    class Config:
        schema_extra = {
            "example": {
                "Name": "Bob",
                "Department": "Research",
                "Stats": [
                    {"Name": "Expertise", "Value": 5},
                    {"Name": "Quality", "Value": 5},
                    {"Name": "Reliability", "Value": 6},
                    {"Name": "Speed", "Value": 3},
                    {"Name": "Capacity", "Value": 2}
                ],
                "preferred_tone": "empowering",
                "autonomy_preference": 7
            }
        }
    
    def get_stat_value(self, stat_name: str) -> int:
        """Get the value of a specific stat"""
        for stat in self.Stats:
            if stat.Name.lower() == stat_name.lower():
                return stat.Value
        return 0
    
    def get_overall_skill_level(self) -> float:
        """Calculate overall skill level as average of all stats"""
        if not self.Stats:
            return 0.0
        return sum(stat.Value for stat in self.Stats) / len(self.Stats)
