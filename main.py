"""
Agent Task Assignment System
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
import json
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
from models.models import RequestBodyRefine, Stat, Agent, Task, RequestBody,RequestBodyRefine,RequestBodyGenerate
from  dotenv import load_dotenv
import uuid
from openai import AsyncOpenAI
import os
load_dotenv()



client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    tags=["Prompt Engineering"],
    summary="Get prompt refinement suggestions",
    description="Get AI-powered suggestions to improve your prompt. Optionally focus on a specific parameter."
)
async def refine_prompt(data: RequestBodyRefine):
    """
    Get suggestions for refining a prompt.
    
    This endpoint:
    - Analyzes the current prompt 
    - Generates an improved version based on the calrity so defualt is 5 which means clear 5> means more clear and 5< means less clear
    - Explains what was improved
    - Estimates quality improvement
    """
    calarity = data.focus_parameter[1].Value
    focus_summary = ", ".join([f"{f.Name}: {f.Value}" for f in data.focus_parameter])

    system_message = (
        "You are a prompt refinement assistant you will refine prompt only if calrity param is greater than 5 and in case of less than 5 you have to make prompt more unclear. Return ONLY valid JSON with exactly these keys:\n"
        "{\n"
        f"  \"refined_prompt_text\": string based on the calrity param its current value is {calarity} . if its value is greater than 5 then make it more clear and if its value is less than 5 then make it more unclear then the initial prompt that is {data.Prompt}. (STRICTLY FOLLOW THIS),\n"
        "  \"improvements\": {\n"
        "       \"structure_and_template\": string,\n"
        "       \"clarity_and_empathy\": string,\n"
        "       \"proactive_clarification\": string,\n"
        "       \"output_format_specification\": string,\n"
        "       \"input_definitions\": string,\n"
        "       \"agency_mechanics\": string\n"
        "  },\n"
        "  \"expected_quality_improvement\": number (0-1),\n"
        "  \"agent_feedback\": {\n"
        f"       \"emotion\": string,\n"
        f"       \"feedback_text\": string based on the calrity param its current value is {calarity} . if its value is greater than feedback can be good but in case of less than 5 feedback should have to  be bad,\n"
        "       \"visual_indicator\": string\n"
        "  },\n"
        "  \"suggestions\": [string],\n"
        "  \"is_ready\": boolean\n"
        "}\n"
        f"Generate the refined prompt and detailed feedback including emotion, suggestions, and readiness based on the calrity param its current value is {calarity} . if its value is greater than 5 then make it more clear and if its value is less than 5 then make it more unclear. and it will also effect the agent feedback"
    )



    user_message = f"""
    Agent Name: {data.Agent.Name}
    Task: {data.Task.Title}
    Original Prompt: {data.Prompt}
    Focus Parameters: {focus_summary}
    """

    response = await client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        max_tokens=400
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    return {
        "success": True,
        "refined_prompt_text": result["refined_prompt_text"],
        "improvements": result["improvements"],
        "expected_quality_improvement": result["expected_quality_improvement"],
        "agent_feedback": result["agent_feedback"],
        "suggestions": result["suggestions"],
        "is_ready": result["is_ready"],
        "message": "Prompt refinement suggestions and feedback generated"
    }



@app.post(
    "/tasks/complete",
    response_model=TaskCompletionResponse,
    tags=["Task Management"],
    summary="Complete a task and generate outcomes",
    description="Mark a task as complete and generate outcome options based on prompt quality."
)
async def run_task(data: RequestBody):
    """
    Complete a task and generate outcomes.
    
    This endpoint:
    - Marks the task as completed
    - Evaluates the final prompt quality
    - Generates 2-4 outcome options based on quality
    - Returns agent feedback on the experience
    
    Better prompts lead to better outcomes!
    """
    # ONE ultra-optimized OpenAI call to generate everything
    response = await client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate ALL of the following in ONE JSON:\n\n"
                    "- prompt quality score between 0 and 1\n"
                    "- short agent_feedback sentence (Judge prompt its fine or you need to refine it or need more context)\n"
                    "- short narrative_text\n\n"
                    "Return only JSON with keys: prompt_quality_score, agent_feedback, narrative_text"
                )
            },
            {
                "role": "user",
                "content": f"""
                Agent: {data.Agent.Name}
                Task: {data.Task.Title}
                Prompt: {data.Prompt}
                """
            }
        ],
        max_tokens=150
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    # Build the final output
    output = {
        "success": True,
        "outcome": {
            "task_id": data.Task.ID,
            "agent_name": data.Agent.Name,
            "prompt_quality_score": result["prompt_quality_score"],
            "options": [
                {
                    "option_id": f"outcome_{uuid.uuid4().hex[:8]}",
                    "title": f"Adequate {data.Task.Title}",
                    "description": f"{data.Agent.Name} completed the task with acceptable results.",
                    "outcome_type": "neutral",
                    "stat_modifiers": [
                        {
                            "stat_name": "Productivity",
                            "change": 2,
                            "percentage": True
                        }
                    ],
                    "narrative_text": result["narrative_text"]
                }
            ],
            "agent_feedback": result["agent_feedback"]
        },
        "message": "Task completed successfully"
    }

    return output

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
    status_code=status.HTTP_200_OK,
    tags=["Prompt Engineering"],
    summary="Generate base prompts for a task",
    description="Generate multiple base prompt suggestions for a given task. Optionally customize for a specific agent and style."
)
async def generate_prompts(data: RequestBodyGenerate):
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

    system_prompt = (
        "You are a prompt generation engine. "
        "Given a task description, agent info, and style preference, generate 5 diverse, high-quality task prompts. "
        "Each prompt should be a concise but clear instruction, incorporating style and agent's expertise. "
        "Return ONLY a JSON object with keys: "
        "\"generated_prompts\" (list of 5 strings)."
    )

    user_prompt = f"""
    Task Description: {data.Task.Description}
    Task Title: {data.Task.Title}
    Agent Name: {data.Agent.Name}
    Agent Stats: {', '.join(f'{s.Name}: {s.StatValueObj}' for s in data.Agent.Stats)}
    Style Preference: {data.style_preference}
    """

    response = await client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=350,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    # Build full response
    return {
        "success": True,
        "task_id": data.Task.ID,
        "task_title": data.Task.Title,
        "task_category": "custom",
        "generated_prompts": result["generated_prompts"],
        "prompt_count": len(result["generated_prompts"]),
        "style_applied": data.style_preference,
        "agent_customized": True,
        "generation_method": "template_and_ai",
        "message": f"Generated {len(result['generated_prompts'])} base prompts for your task"
    }

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
