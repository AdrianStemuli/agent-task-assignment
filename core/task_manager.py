"""
Task manager for handling task assignments and lifecycle
"""

from typing import Dict, Optional
import uuid
from datetime import datetime
from models.agent import Agent
from models.task import Task, TaskAssignment, TaskStatus
from models.prompt import Prompt


class TaskManager:
    """Manager for task assignments"""
    
    def __init__(self):
        """Initialize task manager"""
        self.tasks: Dict[str, TaskAssignment] = {}
    
    def create_task_assignment(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt
    ) -> TaskAssignment:
        """
        Create a new task assignment
        
        Args:
            agent: The agent to assign the task to
            task: The task to be assigned
            prompt: The initial prompt for the task
            
        Returns:
            Created TaskAssignment
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        assignment = TaskAssignment(
            task_id=task_id,
            agent_name=agent.Name,
            task=task,
            status=TaskStatus.PENDING,
            assigned_at=datetime.utcnow()
        )
        
        self.tasks[task_id] = assignment
        return assignment
    
    def get_task(self, task_id: str) -> Optional[TaskAssignment]:
        """
        Get a task assignment by ID
        
        Args:
            task_id: ID of the task
            
        Returns:
            TaskAssignment if found, None otherwise
        """
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        Update the status of a task
        
        Args:
            task_id: ID of the task
            status: New status
            
        Returns:
            True if updated, False if task not found
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        task.status = status
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
        
        return True
    
    def get_agent_tasks(self, agent_name: str) -> list[TaskAssignment]:
        """
        Get all tasks for a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of TaskAssignments for the agent
        """
        return [
            task for task in self.tasks.values()
            if task.agent_name == agent_name
        ]
    
    def get_pending_tasks(self) -> list[TaskAssignment]:
        """
        Get all pending tasks
        
        Returns:
            List of pending TaskAssignments
        """
        return [
            task for task in self.tasks.values()
            if task.status == TaskStatus.PENDING
        ]
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task assignment
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if deleted, False if task not found
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def get_all_tasks(self) -> list[TaskAssignment]:
        """
        Get all task assignments
        
        Returns:
            List of all TaskAssignments
        """
        return list(self.tasks.values())
