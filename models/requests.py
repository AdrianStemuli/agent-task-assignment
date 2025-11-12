"""
Request models for API endpoints
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Any


class TaskAssignmentRequest(BaseModel):
    """Request to assign a task to an agent"""
    Agent: Any = Field(
        ..., 
        description="The agent to assign the task to (Unity object or string)",
        example={
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Analyst",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 8},
                {"Name": "Speed", "StatValueObj": 6},
                {"Name": "Reliability", "StatValueObj": 8},
                {"Name": "Quality", "StatValueObj": 7},
                {"Name": "Capacity", "StatValueObj": 3},
                {"Name": "TokenMultiplier", "StatValueObj": 1.5}
            ]
        }
    )
    Task: Any = Field(
        ..., 
        description="The task to be assigned (Unity object or string)",
        example={
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write email",
            "Description": "Write an email to Alice"
        }
    )
    Prompt: Any = Field(
        ..., 
        description="The initial prompt for the task",
        example="Please write a professional email to Alice regarding the quarterly report. Make sure to include all necessary details and maintain a friendly tone."
    )
    
    class Config:
        arbitrary_types_allowed = True


class PromptEvaluationRequest(BaseModel):
    """Request to evaluate a prompt's quality"""
    Agent: Any = Field(
        ..., 
        description="The agent who will receive the prompt (Unity object or string)",
        example={
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Analyst",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 8},
                {"Name": "Speed", "StatValueObj": 6},
                {"Name": "Reliability", "StatValueObj": 8},
                {"Name": "Quality", "StatValueObj": 7},
                {"Name": "Capacity", "StatValueObj": 3},
                {"Name": "TokenMultiplier", "StatValueObj": 1.5}
            ]
        }
    )
    Task: Any = Field(
        ..., 
        description="The task context (Unity object or string)",
        example={
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write email",
            "Description": "Write an email to Alice"
        }
    )
    Prompt: Any = Field(
        ..., 
        description="The prompt to evaluate",
        example="Please write a professional email to Alice regarding the quarterly report."
    )
    
    class Config:
        arbitrary_types_allowed = True


class PromptRefinementRequest(BaseModel):
    """Request to get suggestions for improving a prompt"""
    Agent: Any = Field(
        ..., 
        description="The agent who will receive the prompt (Unity object or string)",
        example={
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Analyst",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 8},
                {"Name": "Speed", "StatValueObj": 6},
                {"Name": "Reliability", "StatValueObj": 8},
                {"Name": "Quality", "StatValueObj": 7},
                {"Name": "Capacity", "StatValueObj": 3},
                {"Name": "TokenMultiplier", "StatValueObj": 1.5}
            ]
        }
    )
    Task: Any = Field(
        ..., 
        description="The task context (Unity object or string)",
        example={
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write email",
            "Description": "Write an email to Alice"
        }
    )
    Prompt: Any = Field(
        ..., 
        description="The current prompt to refine",
        example="Write an email to Alice"
    )
    focus_parameter: Optional[str] = Field(
        default=None,
        description="Specific parameter to focus on (Clarity, Context, Tone, Agency, Empathy)",
        example="Clarity"
    )
    
    class Config:
        arbitrary_types_allowed = True


class TaskCompletionRequest(BaseModel):
    """Request to complete a task and generate outcomes"""
    task_id: str = Field(
        ..., 
        description="ID of the task to complete",
        example="task_43adea39dcf7"
    )
    Agent: Any = Field(
        ..., 
        description="The agent who completed the task (Unity object or string)",
        example={
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Analyst",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 8},
                {"Name": "Speed", "StatValueObj": 6},
                {"Name": "Reliability", "StatValueObj": 8},
                {"Name": "Quality", "StatValueObj": 7},
                {"Name": "Capacity", "StatValueObj": 3},
                {"Name": "TokenMultiplier", "StatValueObj": 1.5}
            ]
        }
    )
    Task: Any = Field(
        ..., 
        description="The completed task (Unity object or string)",
        example={
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write email",
            "Description": "Write an email to Alice"
        }
    )
    Prompt: Any = Field(
        ..., 
        description="The final prompt that was used",
        example="Please write a professional email to Alice regarding the quarterly report."
    )
    
    class Config:
        arbitrary_types_allowed = True


class PromptGenerationRequest(BaseModel):
    """Request to generate base prompts for a task"""
    Task: Any = Field(
        ..., 
        description="The task to generate prompts for (Unity object or string)",
        example={
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write Marketing Email",
            "Description": "Create an email campaign to increase customer retention"
        }
    )
    Agent: Optional[Any] = Field(
        default=None,
        description="Optional agent to customize prompts for (Unity object or string)",
        example={
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Marketing Specialist",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 7},
                {"Name": "Creativity", "StatValueObj": 9},
                {"Name": "Communication", "StatValueObj": 8}
            ]
        }
    )
    style_preference: Optional[str] = Field(
        default=None,
        description="Optional style preference for the prompts",
        example="professional"
    )
    
    class Config:
        arbitrary_types_allowed = True
