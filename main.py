"""
Agent Task Assignment System
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
from parallel import generate_prompt_quality, generate_agent_feedback, generate_narrative

from config import settings
from models.requests import (
    TaskAssignmentRequest,
    PromptEvaluationRequest,
    PromptRefinementRequest,
    TaskCompletionRequest,
    PromptGenerationRequest
)
import asyncio
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
from services.parallel_outcome_generator import ParallelOutcomeGenerator
from services.prompt_generator import PromptGenerator
from models.models import Stat, Agent, Task, RequestBody
from  dotenv import load_dotenv
import uuid

load_dotenv()


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

# Global service instances
task_manager = TaskManager()
openai_service = None
prompt_evaluator = None
outcome_generator = None
parallel_outcome_generator = None
prompt_generator = None


@asynccontextmanager
async def Lifecycle(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global openai_service, prompt_evaluator, outcome_generator, parallel_outcome_generator, prompt_generator
    
    # Startup
    try:
        openai_service = OpenAIService()
        prompt_evaluator = PromptEvaluator(openai_service)
        outcome_generator = OutcomeGenerator(openai_service)
        parallel_outcome_generator = ParallelOutcomeGenerator(openai_service)
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
    lifespan=Lifecycle
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
    response  = run_task(request)
    return response
    # if not parallel_outcome_generator:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="OpenAI service not configured. Set OPENAI_API_KEY environment variable."
    #     )
    
    # try:
    #     # Convert inputs to proper objects
    #     agent = convert_agent_input(request.Agent)
    #     task_obj = convert_task_input(request.Task)
    #     prompt = convert_prompt_input(request.Prompt)
        
    #     # Use the Task's ID directly
    #     task_id = task_obj.ID
    #     if not task_id:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Task object must contain an ID for completion"
    #         )
        
    #     # Verify task exists
    #     task = task_manager.get_task(task_id)
    #     if not task:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=f"Task {task_id} not found"
    #         )
        
    #     # Run prompt evaluation and outcome generation in parallel
    #     import asyncio
        
    #     # Create tasks for parallel execution
    #     evaluation_task = prompt_evaluator.evaluate_prompt_with_ai(
    #         prompt=prompt,
    #         agent=agent,
    #         task=task_obj
    #     )
        
    #     # For outcome generation, we'll use a base quality score initially
    #     # and then adjust if needed based on the evaluation
    #     base_quality_score = prompt_evaluator.calculate_base_scores(prompt, agent, task_obj)
    #     estimated_quality = sum(base_quality_score.values()) / len(base_quality_score)
        
    #     outcome_task = parallel_outcome_generator.generate_outcomes(
    #         task_id=task_id,
    #         agent=agent,
    #         task=task_obj,
    #         prompt=prompt,
    #         quality_score=estimated_quality
    #     )
        
    #     # Wait for both to complete
    #     (quality_metrics, _, _), outcome = await asyncio.gather(evaluation_task, outcome_task)
        
    #     # Update the outcome with the actual quality score
    #     outcome.prompt_quality_score = quality_metrics.overall_score
        
    #     # Update task status
    #     task_manager.update_task_status(task_id, task.status.__class__.COMPLETED)
        
    #     return TaskCompletionResponse(
    #         success=True,
    #         outcome=outcome,
    #         message="Task completed successfully"
    #     )
        
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Failed to complete task: {str(e)}"
    #     )


@app.post("/run-task")
async def run_task(data: TaskCompletionRequest):

    agent = convert_agent_input(data.Agent)
    task = convert_task_input(data.Task)
    prompt = convert_prompt_input(data.Prompt)
    


    task_id = task.ID
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task object must contain an ID for completion"
        )
        
    # Verify task exists
    task_obj = task_manager.get_task(task_id)
    if not task_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    (
        prompt_quality,
        agent_feedback,
        narrative_text,
    ) = await asyncio.gather(
        generate_prompt_quality(prompt),
        generate_agent_feedback(agent.Name, task.Title, prompt),
        generate_narrative(task.Title, agent.Name)
    )

    outcome = {
        "task_id": task.ID,
        "agent_name": agent.Name,
        "prompt_quality_score": prompt_quality,
        "options": [
            {
                "option_id": f"outcome_{uuid.uuid4().hex[:8]}",
                "title": f"Adequate {task.Title}",
                "description": f"{agent.Name} completed the task with acceptable results.",
                "outcome_type": "neutral",
                "stat_modifiers": [
                    {
                        "stat_name": "Productivity",
                        "change": 2,
                        "percentage": True
                    }
                ],
                "narrative_text": narrative_text
            }
        ],
        "agent_feedback": agent_feedback
    }

    return {
        "success": True,
        "outcome": outcome,
        "message": "Task completed successfully"
    }


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
    response_model=Dict[str, Any],
    tags=["Agent Management"],
    summary="Get tasks for a specific agent",
    description="Retrieve all tasks assigned to a specific agent by name."
)
async def get_agent_tasks(agent_name: str) -> Dict[str, Any]:
    """
    Get all tasks assigned to a specific agent
    
    Args:
        agent_name: Name of the agent to get tasks for
        
    Returns:
        Dictionary containing agent name, tasks, and total count
    """
    tasks = task_manager.get_tasks_by_agent(agent_name)
    
    return {
        "agent_name": agent_name,
        "tasks": tasks,
        "total": len(tasks)
    }


@app.post(
    "/benchmark/task-completion",
    response_model=Dict[str, Any],
    tags=["Testing"],
    summary="Benchmark task completion performance",
    description="Compare performance between original and optimized task completion approaches."
)
async def benchmark_task_completion(request: TaskCompletionRequest) -> Dict[str, Any]:
    """
    Benchmark task completion performance
    
    This endpoint compares the original sequential approach with the new parallel approach
    to demonstrate performance improvements.
    """
    if not parallel_outcome_generator or not outcome_generator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI service not configured. Set OPENAI_API_KEY environment variable."
        )
    
    import time
    import asyncio
    
    try:
        # Convert inputs to proper objects
        agent = convert_agent_input(request.Agent)
        task_obj = convert_task_input(request.Task)
        prompt = convert_prompt_input(request.Prompt)
        
        # Ensure task has an ID for the benchmark
        if not task_obj.ID:
            import uuid
            task_obj.ID = str(uuid.uuid4())
        
        # Test original sequential approach
        start_time = time.time()
        
        quality_metrics_orig, _, _ = await prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task_obj
        )
        
        outcome_orig = await outcome_generator.generate_outcomes(
            task_id=task_obj.ID,
            agent=agent,
            task=task_obj,
            prompt=prompt,
            quality_score=quality_metrics_orig.overall_score
        )
        
        original_duration = time.time() - start_time
        
        # Test new parallel approach
        start_time = time.time()
        
        evaluation_task = prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task_obj
        )
        
        base_quality_score = prompt_evaluator.calculate_base_scores(prompt, agent, task_obj)
        estimated_quality = sum(base_quality_score.values()) / len(base_quality_score)
        
        outcome_task = parallel_outcome_generator.generate_outcomes(
            task_id=task_obj.ID,
            agent=agent,
            task=task_obj,
            prompt=prompt,
            quality_score=estimated_quality
        )
        
        (quality_metrics_new, _, _), outcome_new = await asyncio.gather(evaluation_task, outcome_task)
        outcome_new.prompt_quality_score = quality_metrics_new.overall_score
        
        parallel_duration = time.time() - start_time
        
        # Calculate improvement
        improvement = ((original_duration - parallel_duration) / original_duration) * 100
        
        return {
            "benchmark_results": {
                "original_duration_seconds": round(original_duration, 3),
                "parallel_duration_seconds": round(parallel_duration, 3),
                "performance_improvement_percent": round(improvement, 1),
                "speedup_factor": round(original_duration / parallel_duration, 2)
            },
            "quality_comparison": {
                "original_quality_score": round(quality_metrics_orig.overall_score, 3),
                "parallel_quality_score": round(quality_metrics_new.overall_score, 3),
                "quality_difference": round(abs(quality_metrics_orig.overall_score - quality_metrics_new.overall_score), 3)
            },
            "outcome_comparison": {
                "original_options_count": len(outcome_orig.options),
                "parallel_options_count": len(outcome_new.options),
                "sample_parallel_option": {
                    "title": outcome_new.options[0].title if outcome_new.options else "None",
                    "outcome_type": outcome_new.options[0].outcome_type.value if outcome_new.options else "None"
                }
            },
            "recommendation": "Use parallel approach" if improvement > 10 else "Marginal improvement" if improvement > 0 else "Original approach faster"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )
