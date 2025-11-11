"""
Response models for API endpoints
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class TaskAssignmentResponse(BaseModel):
    """Response after assigning a task"""
    success: bool = Field(..., description="Whether the assignment was successful")
    task_assignment: Any = Field(..., description="The created task assignment")
    initial_feedback: str = Field(
        ...,
        description="Initial feedback from the agent about the task"
    )
    message: str = Field(..., description="Human-readable message")
    
    class Config:
        arbitrary_types_allowed = True


class PromptQualityMetrics(BaseModel):
    """Detailed metrics about prompt quality"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score (0-1)")
    clarity_score: float = Field(..., ge=0.0, le=1.0, description="How clear and specific the prompt is")
    context_score: float = Field(..., ge=0.0, le=1.0, description="How much context is provided")
    tone_score: float = Field(..., ge=0.0, le=1.0, description="How appropriate the tone is")
    agency_score: float = Field(..., ge=0.0, le=1.0, description="How well it balances direction and freedom")
    empathy_score: float = Field(..., ge=0.0, le=1.0, description="How empathetic the prompt is")
    agent_fit_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How well the prompt fits the agent's preferences"
    )


class AgentFeedbackResponse(BaseModel):
    """Agent's reaction and feedback to a prompt"""
    emotion: str = Field(..., description="Agent's emotional reaction (e.g., 'happy', 'confused', 'motivated')")
    feedback_text: str = Field(..., max_length=300, description="Textual feedback from the agent")
    visual_indicator: str = Field(
        ...,
        description="Visual indicator for UI (e.g., 'thumbs_up', 'question_mark', 'star')"
    )


class PromptEvaluationResponse(BaseModel):
    """Response with prompt quality evaluation"""
    success: bool = Field(..., description="Whether the evaluation was successful")
    quality_metrics: PromptQualityMetrics = Field(..., description="Detailed quality metrics")
    agent_feedback: AgentFeedbackResponse = Field(..., description="Agent's feedback")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improving the prompt"
    )
    is_ready: bool = Field(
        ...,
        description="Whether the prompt is good enough to proceed"
    )
    message: str = Field(..., description="Human-readable message")
    

class PromptRefinementResponse(BaseModel):
    """Response with refined prompt suggestions"""
    success: bool = Field(..., description="Whether the refinement was successful")
    refined_prompt_text: str = Field(..., description="Suggested refined prompt text")
    improvements: Dict[str, str] = Field(
        ...,
        description="Map of parameter names to improvement descriptions"
    )
    expected_quality_improvement: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Expected improvement in quality score"
    )
    message: str = Field(..., description="Human-readable message")
    

class TaskCompletionResponse(BaseModel):
    """Response after completing a task with outcomes"""
    success: bool = Field(..., description="Whether the completion was successful")
    outcome: Any = Field(..., description="The task outcome with options")
    message: str = Field(..., description="Human-readable message")
    
    class Config:
        arbitrary_types_allowed = True
    

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
    
