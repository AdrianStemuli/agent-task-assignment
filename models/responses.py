"""
Response models for API endpoints
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.task import TaskAssignment


class TaskAssignmentResponse(BaseModel):
    """Response after assigning a task"""
    success: bool = Field(..., description="Whether the assignment was successful")
    task_assignment: Any = Field(
        ...,
        description="The created task assignment with task_id and details"
    )
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


class PromptGenerationResponse(BaseModel):
    """Response with generated base prompts for a task"""
    success: bool = Field(..., description="Whether the generation was successful")
    task_id: str = Field(..., description="ID of the task")
    task_title: str = Field(..., description="Title of the task")
    task_category: str = Field(..., description="Category of the task")
    generated_prompts: List[str] = Field(
        ..., 
        description="List of generated base prompts",
        min_items=1,
        max_items=5
    )
    prompt_count: int = Field(..., description="Number of prompts generated")
    style_applied: str = Field(..., description="Style preference that was applied")
    agent_customized: bool = Field(..., description="Whether prompts were customized for a specific agent")
    generation_method: str = Field(..., description="Method used for generation (template_only, template_and_ai)")
    message: str = Field(..., description="Human-readable message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "task_id": "e84f8439-8072-4b02-85b0-44d0dad335b7",
                "task_title": "Write Marketing Email",
                "task_category": "email_campaign",
                "generated_prompts": [
                    "Please write a professional email campaign for creating an email campaign to increase customer retention. Include a compelling subject line, clear value proposition, and strong call-to-action.",
                    "Create an engaging email marketing campaign about creating an email campaign to increase customer retention. Focus on customer benefits and include personalization elements.",
                    "Draft a persuasive email campaign for creating an email campaign to increase customer retention. Use a conversational tone and highlight key benefits for the target audience."
                ],
                "prompt_count": 3,
                "style_applied": "professional",
                "agent_customized": True,
                "generation_method": "template_and_ai",
                "message": "Generated 3 base prompts for your task"
            }
        }
    

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
    
