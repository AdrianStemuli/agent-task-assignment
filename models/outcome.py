"""
Outcome models for task completion results
"""

from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum


class OutcomeType(str, Enum):
    """Type of outcome effect"""
    BUFF = "buff"
    DEBUFF = "debuff"
    NEUTRAL = "neutral"


class StatModifier(BaseModel):
    """Modifier for a specific game stat"""
    stat_name: str
    change: int
    percentage: bool = False
    

class OutcomeOption(BaseModel):
    """A single outcome option that the player can choose"""
    option_id: str
    title: str
    description: str
    outcome_type: OutcomeType
    stat_modifiers: List[StatModifier] = []
    narrative_text: str
    

class TaskOutcome(BaseModel):
    """Complete outcome of a task with multiple options"""
    task_id: str
    agent_name: str
    prompt_quality_score: float
    options: List[OutcomeOption]
    agent_feedback: str
    
