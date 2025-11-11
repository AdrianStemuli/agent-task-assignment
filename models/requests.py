"""
Request models for API endpoints
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Any


class TaskAssignmentRequest(BaseModel):
    """Request to assign a task to an agent"""
    Agent: Any = Field(..., description="The agent to assign the task to")
    Task: Any = Field(..., description="The task to be assigned")
    Prompt: Any = Field(..., description="The initial prompt for the task")
    
    class Config:
        arbitrary_types_allowed = True


class PromptEvaluationRequest(BaseModel):
    """Request to evaluate a prompt's quality"""
    Agent: Any = Field(..., description="The agent who will receive the prompt")
    Task: Any = Field(..., description="The task context")
    Prompt: Any = Field(..., description="The prompt to evaluate")
    
    class Config:
        arbitrary_types_allowed = True


class PromptRefinementRequest(BaseModel):
    """Request to get suggestions for improving a prompt"""
    Agent: Any = Field(..., description="The agent who will receive the prompt")
    Task: Any = Field(..., description="The task context")
    Prompt: Any = Field(..., description="The current prompt to refine")
    focus_parameter: Optional[str] = Field(
        default=None,
        description="Specific parameter to focus on (Clarity, Context, Tone, Agency, Empathy)"
    )
    
    class Config:
        arbitrary_types_allowed = True


class TaskCompletionRequest(BaseModel):
    """Request to complete a task and generate outcomes"""
    task_id: str = Field(..., description="ID of the task to complete")
    Agent: Any = Field(..., description="The agent who completed the task")
    Task: Any = Field(..., description="The completed task")
    Prompt: Any = Field(..., description="The final prompt that was used")
    
    class Config:
        arbitrary_types_allowed = True
