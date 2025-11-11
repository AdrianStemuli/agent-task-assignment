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
    TaskCompletionRequest
)
from models.responses import (
    TaskAssignmentResponse,
    PromptEvaluationResponse,
    PromptRefinementResponse,
    TaskCompletionResponse,
    ErrorResponse
)
from services.openai_service import OpenAIService
from services.prompt_evaluator import PromptEvaluator
from services.outcome_generator import OutcomeGenerator
from core.task_manager import TaskManager


# Global instances
task_manager = TaskManager()
openai_service = None
prompt_evaluator = None
outcome_generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global openai_service, prompt_evaluator, outcome_generator
    
    # Startup
    try:
        openai_service = OpenAIService()
        prompt_evaluator = PromptEvaluator(openai_service)
        outcome_generator = OutcomeGenerator(openai_service)
        print(f"✓ {settings.app_name} initialized successfully")
        print(f"✓ OpenAI Model: {settings.openai_model}")
    except ValueError as e:
        print(f"⚠ Warning: {str(e)}")
        print("⚠ OpenAI features will not be available. Set OPENAI_API_KEY to enable.")
    
    yield
    
    # Shutdown
    print(f"✓ {settings.app_name} shutting down")


app = FastAPI(
    title=settings.app_name,
    description="""
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
    description="Create a new task assignment with an initial prompt. Returns the task assignment and initial agent feedback."
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
        # Handle both string and object inputs for backward compatibility
        from models.agent import Agent, AgentStat, Department
        from models.task import Task, TaskCategory
        from models.prompt import Prompt
        
        # Convert string inputs to proper objects if needed
        if isinstance(request.Agent, str):
            # Create a simple agent from string
            agent = Agent(
                Name=request.Agent,
                Department=Department.RESEARCH,
                Stats=[
                    AgentStat(Name="Expertise", Value=5),
                    AgentStat(Name="Quality", Value=5),
                    AgentStat(Name="Reliability", Value=5),
                    AgentStat(Name="Speed", Value=5),
                    AgentStat(Name="Capacity", Value=5)
                ]
            )
        else:
            agent = request.Agent
            
        if isinstance(request.Task, str):
            # Create a simple task from string
            task = Task(
                Title="Task",
                Description=request.Task,
                Category=TaskCategory.CUSTOM
            )
        else:
            task = request.Task
            
        if isinstance(request.Prompt, str):
            # Create a simple prompt from string
            prompt = Prompt(
                Text=request.Prompt,
                Parameters=[]
            )
        else:
            prompt = request.Prompt
        
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
        # Handle both string and object inputs for backward compatibility
        from models.agent import Agent, AgentStat, Department
        from models.task import Task, TaskCategory
        from models.prompt import Prompt
        
        # Convert string inputs to proper objects if needed
        if isinstance(request.Agent, str):
            agent = Agent(
                Name=request.Agent,
                Department=Department.RESEARCH,
                Stats=[
                    AgentStat(Name="Expertise", Value=5),
                    AgentStat(Name="Quality", Value=5),
                    AgentStat(Name="Reliability", Value=5),
                    AgentStat(Name="Speed", Value=5),
                    AgentStat(Name="Capacity", Value=5)
                ]
            )
        else:
            agent = request.Agent
            
        if isinstance(request.Task, str):
            task = Task(
                Title="Task",
                Description=request.Task,
                Category=TaskCategory.CUSTOM
            )
        else:
            task = request.Task
            
        if isinstance(request.Prompt, str):
            prompt = Prompt(
                Text=request.Prompt,
                Parameters=[]
            )
        else:
            prompt = request.Prompt
        
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
        # Handle both string and object inputs for backward compatibility
        from models.agent import Agent, AgentStat, Department
        from models.task import Task, TaskCategory
        from models.prompt import Prompt
        
        # Convert string inputs to proper objects if needed
        if isinstance(request.Agent, str):
            agent = Agent(
                Name=request.Agent,
                Department=Department.RESEARCH,
                Stats=[
                    AgentStat(Name="Expertise", Value=5),
                    AgentStat(Name="Quality", Value=5),
                    AgentStat(Name="Reliability", Value=5),
                    AgentStat(Name="Speed", Value=5),
                    AgentStat(Name="Capacity", Value=5)
                ]
            )
        else:
            agent = request.Agent
            
        if isinstance(request.Task, str):
            task = Task(
                Title="Task",
                Description=request.Task,
                Category=TaskCategory.CUSTOM
            )
        else:
            task = request.Task
            
        if isinstance(request.Prompt, str):
            prompt = Prompt(
                Text=request.Prompt,
                Parameters=[]
            )
        else:
            prompt = request.Prompt
        
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
        # Handle both string and object inputs for backward compatibility
        from models.agent import Agent, AgentStat, Department
        from models.task import Task, TaskCategory
        from models.prompt import Prompt
        
        # Convert string inputs to proper objects if needed
        if isinstance(request.Agent, str):
            agent = Agent(
                Name=request.Agent,
                Department=Department.RESEARCH,
                Stats=[
                    AgentStat(Name="Expertise", Value=5),
                    AgentStat(Name="Quality", Value=5),
                    AgentStat(Name="Reliability", Value=5),
                    AgentStat(Name="Speed", Value=5),
                    AgentStat(Name="Capacity", Value=5)
                ]
            )
        else:
            agent = request.Agent
            
        if isinstance(request.Task, str):
            task_obj = Task(
                Title="Task",
                Description=request.Task,
                Category=TaskCategory.CUSTOM
            )
        else:
            task_obj = request.Task
            
        if isinstance(request.Prompt, str):
            prompt = Prompt(
                Text=request.Prompt,
                Parameters=[]
            )
        else:
            prompt = request.Prompt
        
        # Verify task exists
        task = task_manager.get_task(request.task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {request.task_id} not found"
            )
        
        # Evaluate final prompt quality
        quality_metrics, _, _ = await prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task_obj
        )
        
        # Generate outcomes
        outcome = await outcome_generator.generate_outcomes(
            task_id=request.task_id,
            agent=agent,
            task=task_obj,
            prompt=prompt,
            quality_score=quality_metrics.overall_score
        )
        
        # Update task status
        task_manager.update_task_status(request.task_id, task.status.__class__.COMPLETED)
        
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
