"""
Agent Task Assignment System
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from models.requests import (
    TaskAssignmentRequest,
    PromptEvaluationRequest,
    PromptRefinementRequest,
    TaskCompletionRequest,
    PromptGenerationRequest
)
from models.responses import (
    TaskAssignmentResponse,
    PromptEvaluationResponse,
    PromptRefinementResponse,
    TaskCompletionResponse,
    PromptGenerationResponse,
    ErrorResponse
)
from core.task_manager import TaskManager
from services.openai_service import OpenAIService
from services.prompt_evaluator import PromptEvaluator
from services.outcome_generator import OutcomeGenerator
from services.prompt_generator import PromptGenerator

# Utility functions for converting inputs
def convert_agent_input(agent_input):
    """Convert agent input (string, dict, or Agent) to Agent object"""
    from models.agent import Agent, AgentStat, Department
    import uuid
    
    if isinstance(agent_input, str):
        # Create a simple agent from string
        return Agent(
            ID=str(uuid.uuid4()),
            Name=agent_input,
            Department=Department.RESEARCH,
            Stats=[
                AgentStat(Name="Expertise", StatValueObj=5),
                AgentStat(Name="Quality", StatValueObj=5),
                AgentStat(Name="Reliability", StatValueObj=5),
                AgentStat(Name="Speed", StatValueObj=5),
                AgentStat(Name="Capacity", StatValueObj=5),
                AgentStat(Name="TokenMultiplier", StatValueObj=1.0)
            ]
        )
    elif isinstance(agent_input, dict):
        # Convert Unity dictionary to Agent object
        stats = [AgentStat(**stat) for stat in agent_input.get("Stats", [])]
        
        # Handle Department - default to RESEARCH if not provided
        dept_str = agent_input.get("Department")
        if dept_str:
            try:
                department = Department(dept_str)
            except ValueError:
                department = Department.RESEARCH
        else:
            department = Department.RESEARCH
            
        return Agent(
            ID=agent_input.get("ID", ""),
            Name=agent_input.get("Name", ""),
            Stats=stats,
            Department=department,
            preferred_tone=agent_input.get("preferred_tone", "balanced"),
            autonomy_preference=agent_input.get("autonomy_preference", 5)
        )
    else:
        # Already an Agent object
        return agent_input

def convert_task_input(task_input):
    """Convert task input (string, dict, or Task) to Task object"""
    from models.task import Task, TaskCategory
    import uuid
    
    if isinstance(task_input, str):
        # Create a simple task from string
        return Task(
            ID=str(uuid.uuid4()),
            Title="Task",
            Description=task_input,
            Category=TaskCategory.CUSTOM
        )
    elif isinstance(task_input, dict):
        # Convert Unity dictionary to Task object
        # Handle Category - default to CUSTOM if not provided or invalid
        cat_str = task_input.get("Category", "custom")
        try:
            category = TaskCategory(cat_str)
        except ValueError:
            category = TaskCategory.CUSTOM
            
        return Task(
            ID=task_input.get("ID", ""),
            Title=task_input.get("Title", ""),
            Description=task_input.get("Description", ""),
            Category=category
        )
    else:
        # Already a Task object
        return task_input

def convert_prompt_input(prompt_input):
    """Convert prompt input (string or Prompt) to Prompt object"""
    from models.prompt import Prompt
    
    if isinstance(prompt_input, str):
        # Create a simple prompt from string
        return Prompt(
            Text=prompt_input,
            Parameters=[]
        )
    else:
        # Already a Prompt object
        return prompt_input

# Import models for proper initialization
from models.agent import Agent
from models.task import Task  
from models.prompt import Prompt

# Rebuild models to resolve any forward references
Task.model_rebuild()
Agent.model_rebuild()
Prompt.model_rebuild()

# Global instances
task_manager = TaskManager()
openai_service = None
prompt_evaluator = None
outcome_generator = None
prompt_generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global openai_service, prompt_evaluator, outcome_generator, prompt_generator
    
    # Startup
    try:
        openai_service = OpenAIService()
        prompt_evaluator = PromptEvaluator(openai_service)
        outcome_generator = OutcomeGenerator(openai_service)
        prompt_generator = PromptGenerator(openai_service)
        print("✓ Agent Task Assignment System initialized successfully")
        print(f"✓ OpenAI Model: {openai_service.model}")
    except Exception as e:
        print(f"⚠ Warning: OpenAI service not configured: {e}")
        print("  Some features will be limited without OpenAI API key")
        # Initialize prompt generator without OpenAI for template-only mode
        prompt_generator = PromptGenerator(None)
    
    yield
    
    # Shutdown
    print("✓ Agent Task Assignment System shutting down")


app = FastAPI(
    title=settings.app_name,
    description="""
{{ ... }}
    Agent Task Assignment System with Prompt Engineering
    
    This system enables:
    - Assigning tasks to agents with customizable prompts
    - Real-time prompt quality evaluation
    - AI-powered prompt refinement suggestions
    - Dynamic outcome generation based on prompt quality
    - Educational feedback for prompt engineering learning
    
    ## Workflow
    1. **Assign Task**: Create a task assignment with initial prompt
    2. **Evaluate Prompt**: Get real-time feedback on prompt quality
    3. **Refine Prompt**: Get AI suggestions to improve the prompt
    4. **Complete Task**: Generate outcomes based on final prompt quality
    
    ## Prompt Parameters
    - **Clarity**: Vague (1) → Precise (10)
    - **Context**: Minimal (1) → Rich (10)
    - **Tone**: Directive (1) → Empowering (10)
    - **Agency**: Strict Direction (1) → Freedom (10)
    - **Empathy**: None (1) → High (10)
    """,
    version=settings.app_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": settings.app_name,
        "status": "active",
        "version": settings.app_version,
        "openai_enabled": openai_service is not None
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "openai_configured": settings.openai_api_key is not None,
        "openai_model": settings.openai_model,
        "active_tasks": len(task_manager.get_all_tasks()),
        "pending_tasks": len(task_manager.get_pending_tasks())
    }
    return health_status


@app.post(
    "/tasks/assign",
    response_model=TaskAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Task Management"],
    summary="Assign a task to an agent",
    description="""Create a new task assignment with an initial prompt. 
    
    **Preferred Format (Unity Objects):**
    ```json
    {
      "Agent": {
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
      },
      "Task": {
        "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
        "Title": "Write email",
        "Description": "Write an email to Alice"
      },
      "Prompt": "Please write a professional email to Alice regarding the quarterly report."
    }
    ```
    
    **Legacy Format (Strings):** Also supported for backward compatibility.
    
    Returns the task assignment and initial agent feedback."""
)
async def assign_task(request: TaskAssignmentRequest) -> TaskAssignmentResponse:
    """
    Assign a task to an agent with an initial prompt.
    
    This endpoint:
    - Creates a new task assignment
    - Stores it in the task manager
    - Returns initial feedback from the agent
    """
    try:
        # Convert inputs to proper objects
        agent = convert_agent_input(request.Agent)
        task = convert_task_input(request.Task)
        prompt = convert_prompt_input(request.Prompt)
        
        # Create task assignment
        assignment = task_manager.create_task_assignment(
            agent=agent,
            task=task,
            prompt=prompt
        )
        
        # Generate initial feedback
        agent_name = agent.Name if hasattr(agent, 'Name') else str(agent)
        initial_feedback = f"{agent_name} has received the task and is ready to begin."
        
        return TaskAssignmentResponse(
            success=True,
            task_assignment=assignment,
            initial_feedback=initial_feedback,
            message=f"Task successfully assigned to {agent_name}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign task: {str(e)}"
        )


@app.post(
    "/prompts/evaluate",
    response_model=PromptEvaluationResponse,
    tags=["Prompt Engineering"],
    summary="Evaluate prompt quality",
    description="Evaluate a prompt's quality and get agent feedback. Returns detailed metrics and suggestions for improvement."
)
async def evaluate_prompt(request: PromptEvaluationRequest) -> PromptEvaluationResponse:
    """
    Evaluate the quality of a prompt.
    
    This endpoint:
    - Analyzes the prompt against best practices
    - Evaluates fit with agent preferences
    - Provides detailed quality metrics
    - Returns agent feedback and suggestions
    """
    if not prompt_evaluator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Convert inputs to proper objects
        agent = convert_agent_input(request.Agent)
        task = convert_task_input(request.Task)
        prompt = convert_prompt_input(request.Prompt)
        
        # Evaluate prompt
        quality_metrics, agent_feedback, suggestions = await prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task
        )
        
        # Determine if prompt is ready
        is_ready = quality_metrics.overall_score >= settings.good_prompt_quality_score
        
        return PromptEvaluationResponse(
            success=True,
            quality_metrics=quality_metrics,
            agent_feedback=agent_feedback,
            suggestions=suggestions,
            is_ready=is_ready,
            message="Prompt evaluation completed"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate prompt: {str(e)}"
        )


@app.post(
    "/prompts/refine",
    response_model=PromptRefinementResponse,
    tags=["Prompt Engineering"],
    summary="Get prompt refinement suggestions",
    description="Get AI-powered suggestions to improve your prompt. Optionally focus on a specific parameter."
)
async def refine_prompt(request: PromptRefinementRequest) -> PromptRefinementResponse:
    """
    Get suggestions for refining a prompt.
    
    This endpoint:
    - Analyzes the current prompt
    - Generates an improved version
    - Explains what was improved
    - Estimates quality improvement
    """
    if not prompt_evaluator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Convert inputs to proper objects
        agent = convert_agent_input(request.Agent)
        task = convert_task_input(request.Task)
        prompt = convert_prompt_input(request.Prompt)
        
        # Get refinement suggestions
        refined_text, improvements, expected_improvement = await prompt_evaluator.suggest_refinements(
            prompt=prompt,
            agent=agent,
            task=task,
            focus_parameter=request.focus_parameter
        )
        
        return PromptRefinementResponse(
            success=True,
            refined_prompt_text=refined_text,
            improvements=improvements,
            expected_quality_improvement=expected_improvement,
            message="Prompt refinement suggestions generated"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refine prompt: {str(e)}"
        )


@app.post(
    "/tasks/complete",
    response_model=TaskCompletionResponse,
    tags=["Task Management"],
    summary="Complete a task and generate outcomes",
    description="Mark a task as complete and generate outcome options based on prompt quality."
)
async def complete_task(request: TaskCompletionRequest) -> TaskCompletionResponse:
    """
    Complete a task and generate outcomes.
    
    This endpoint:
    - Marks the task as completed
    - Evaluates the final prompt quality
    - Generates 2-4 outcome options based on quality
    - Returns agent feedback on the experience
    
    Better prompts lead to better outcomes!
    """
    if not outcome_generator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    try:
        # Convert inputs to proper objects
        agent = convert_agent_input(request.Agent)
        task_obj = convert_task_input(request.Task)
        prompt = convert_prompt_input(request.Prompt)
        
        # Use the Task's ID directly
        task_id = task_obj.ID
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task object must contain an ID for completion"
            )
        
        # Verify task exists
        task = task_manager.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Evaluate final prompt quality
        quality_metrics, _, _ = await prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task_obj
        )
        
        # Generate outcomes
        outcome = await outcome_generator.generate_outcomes(
            task_id=task_id,
            agent=agent,
            task=task_obj,
            prompt=prompt,
            quality_score=quality_metrics.overall_score
        )
        
        # Update task status
        task_manager.update_task_status(task_id, task.status.__class__.COMPLETED)
        
        return TaskCompletionResponse(
            success=True,
            outcome=outcome,
            message="Task completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@app.get(
    "/tasks/{task_id}",
    tags=["Task Management"],
    summary="Get task details",
    description="Retrieve details of a specific task assignment."
)
async def get_task(task_id: str):
    """Get details of a specific task"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task


@app.get(
    "/tasks",
    tags=["Task Management"],
    summary="List all tasks",
    description="Get a list of all task assignments."
)
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": task_manager.get_all_tasks(),
        "total": len(task_manager.get_all_tasks()),
        "pending": len(task_manager.get_pending_tasks())
    }


@app.post(
    "/prompts/generate",
    response_model=PromptGenerationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prompt Engineering"],
    summary="Generate base prompts for a task",
    description="Generate multiple base prompt suggestions for a given task. Optionally customize for a specific agent and style."
)
async def generate_base_prompts(request: PromptGenerationRequest) -> PromptGenerationResponse:
    """
    Generate base prompts for a task.
    
    This endpoint:
    - Analyzes the task category and description
    - Generates 3-5 base prompt suggestions
    - Optionally customizes prompts for specific agent capabilities
    - Supports different style preferences (professional, casual, detailed, concise)
    - Uses both template-based and AI-enhanced generation methods
    
    Perfect for getting started with effective task prompts!
    """
    if not prompt_generator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prompt generation service not available."
        )
    
    try:
        # Convert inputs to proper objects
        task = convert_task_input(request.Task)
        agent = convert_agent_input(request.Agent) if request.Agent else None
        
        # Generate base prompts
        result = await prompt_generator.generate_base_prompt(
            task=task,
            agent=agent,
            style_preference=request.style_preference
        )
        
        return PromptGenerationResponse(
            success=True,
            task_id=result["task_id"],
            task_title=result["task_title"],
            task_category=result["task_category"],
            generated_prompts=result["generated_prompts"],
            prompt_count=result["prompt_count"],
            style_applied=result["style_applied"],
            agent_customized=result["agent_customized"],
            generation_method=result["generation_method"],
            message=f"Generated {result['prompt_count']} base prompts for your task"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate prompts: {str(e)}"
        )


@app.get(
    "/agents/{agent_name}/tasks",
    tags=["Task Management"],
    summary="Get agent's tasks",
    description="Get all tasks assigned to a specific agent."
)
async def get_agent_tasks(agent_name: str):
    """Get all tasks for a specific agent"""
    tasks = task_manager.get_agent_tasks(agent_name)
    return {
        "agent_name": agent_name,
        "tasks": tasks,
        "total": len(tasks)
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )
