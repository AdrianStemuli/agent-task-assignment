"""
Task models for the assignment system
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskCategory(str, Enum):
    """Categories of tasks based on department"""
    # Marketing
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_MEDIA = "social_media"
    MARKET_RESEARCH = "market_research"
    
    # HR
    WORKSHOP = "workshop"
    TRAINING = "training"
    RECRUITMENT = "recruitment"
    
    # Engineering
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIX = "bug_fix"
    CODE_REVIEW = "code_review"
    
    # Research
    PRODUCT_RESEARCH = "product_research"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    USER_STUDY = "user_study"
    
    # Design
    UI_DESIGN = "ui_design"
    UX_RESEARCH = "ux_research"
    PROTOTYPE = "prototype"
    
    # Sales
    SALES_PITCH = "sales_pitch"
    CLIENT_MEETING = "client_meeting"
    PROPOSAL = "proposal"
    
    # Operations
    PROCESS_OPTIMIZATION = "process_optimization"
    RESOURCE_PLANNING = "resource_planning"
    REPORTING = "reporting"
    
    # Generic
    CUSTOM = "custom"


class Task(BaseModel):
    """Task model representing work to be done"""
    Title: str
    Description: str
    Category: Optional[TaskCategory] = TaskCategory.CUSTOM
    

class TaskAssignment(BaseModel):
    """Complete task assignment with agent and task details"""
    task_id: str
    agent_name: str
    task: Task
    status: TaskStatus = TaskStatus.PENDING
    assigned_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'assigned_at' not in data or data['assigned_at'] is None:
            data['assigned_at'] = datetime.utcnow()
        super().__init__(**data)
    
