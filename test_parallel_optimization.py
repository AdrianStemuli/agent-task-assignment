"""
Test script to verify the parallel optimization performance
"""

import asyncio
import time
import json
from services.openai_service import OpenAIService
from services.parallel_outcome_generator import ParallelOutcomeGenerator
from services.outcome_generator import OutcomeGenerator
from services.prompt_evaluator import PromptEvaluator
from models.agent import Agent, AgentStat, Department
from models.task import Task, TaskStatus, TaskPriority
from models.prompt import Prompt, PromptParameter, PromptParameterType
from config import settings
import uuid


async def create_test_data():
    """Create test data for performance comparison"""
    
    # Create test agent
    agent = Agent(
        ID=str(uuid.uuid4()),
        Name="Test Analyst",
        Department=Department.RESEARCH,
        Stats=[
            AgentStat(Name="Expertise", StatValueObj=7),
            AgentStat(Name="Quality", StatValueObj=6),
            AgentStat(Name="Reliability", StatValueObj=8),
            AgentStat(Name="Speed", StatValueObj=5),
            AgentStat(Name="Capacity", StatValueObj=6),
        ],
        autonomy_preference=7,
        preferred_tone="professional"
    )
    
    # Create test task
    task = Task(
        ID=str(uuid.uuid4()),
        Title="Quarterly Report Analysis",
        Description="Analyze Q3 financial data and prepare summary for stakeholders",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH,
        assigned_agent_id=agent.ID
    )
    
    # Create test prompt
    prompt = Prompt(
        Text="Please analyze the Q3 financial data and create a comprehensive summary report for our stakeholders. Focus on key metrics, trends, and actionable insights.",
        Parameters=[
            PromptParameter(Name=PromptParameterType.CLARITY, Value=8),
            PromptParameter(Name=PromptParameterType.CONTEXT, Value=7),
            PromptParameter(Name=PromptParameterType.TONE, Value=8),
            PromptParameter(Name=PromptParameterType.AGENCY, Value=6),
            PromptParameter(Name=PromptParameterType.EMPATHY, Value=7),
        ]
    )
    
    return agent, task, prompt


async def test_original_approach(openai_service, agent, task, prompt):
    """Test the original sequential approach"""
    print("Testing original sequential approach...")
    
    start_time = time.time()
    
    # Create services
    prompt_evaluator = PromptEvaluator(openai_service)
    outcome_generator = OutcomeGenerator(openai_service)
    
    # Sequential execution (as in original code)
    quality_metrics, _, _ = await prompt_evaluator.evaluate_prompt_with_ai(
        prompt=prompt,
        agent=agent,
        task=task
    )
    
    outcome = await outcome_generator.generate_outcomes(
        task_id=task.ID,
        agent=agent,
        task=task,
        prompt=prompt,
        quality_score=quality_metrics.overall_score
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Original approach completed in: {duration:.2f} seconds")
    print(f"Quality score: {quality_metrics.overall_score:.3f}")
    print(f"Number of options: {len(outcome.options)}")
    
    return duration, outcome


async def test_parallel_approach(openai_service, agent, task, prompt):
    """Test the new parallel approach"""
    print("\nTesting new parallel approach...")
    
    start_time = time.time()
    
    # Create services
    prompt_evaluator = PromptEvaluator(openai_service)
    parallel_outcome_generator = ParallelOutcomeGenerator(openai_service)
    
    # Parallel execution (as in optimized code)
    evaluation_task = prompt_evaluator.evaluate_prompt_with_ai(
        prompt=prompt,
        agent=agent,
        task=task
    )
    
    # Use base quality score for initial outcome generation
    base_quality_score = prompt_evaluator.calculate_base_scores(prompt, agent, task)
    estimated_quality = sum(base_quality_score.values()) / len(base_quality_score)
    
    outcome_task = parallel_outcome_generator.generate_outcomes(
        task_id=task.ID,
        agent=agent,
        task=task,
        prompt=prompt,
        quality_score=estimated_quality
    )
    
    # Wait for both to complete
    (quality_metrics, _, _), outcome = await asyncio.gather(evaluation_task, outcome_task)
    
    # Update the outcome with the actual quality score
    outcome.prompt_quality_score = quality_metrics.overall_score
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Parallel approach completed in: {duration:.2f} seconds")
    print(f"Quality score: {quality_metrics.overall_score:.3f}")
    print(f"Number of options: {len(outcome.options)}")
    
    return duration, outcome


async def main():
    """Main test function"""
    print("🚀 Starting performance comparison test...\n")
    
    try:
        # Initialize OpenAI service
        openai_service = OpenAIService()
        
        # Create test data
        agent, task, prompt = await create_test_data()
        
        print("Test Configuration:")
        print(f"Agent: {agent.Name} (Skill Level: {agent.get_overall_skill_level():.1f}/10)")
        print(f"Task: {task.Title}")
        print(f"Prompt: {prompt.Text[:100]}...")
        print("=" * 60)
        
        # Test original approach
        original_duration, original_outcome = await test_original_approach(
            openai_service, agent, task, prompt
        )
        
        # Test parallel approach  
        parallel_duration, parallel_outcome = await test_parallel_approach(
            openai_service, agent, task, prompt
        )
        
        # Calculate improvement
        improvement = ((original_duration - parallel_duration) / original_duration) * 100
        
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE RESULTS:")
        print(f"Original approach: {original_duration:.2f}s")
        print(f"Parallel approach: {parallel_duration:.2f}s")
        print(f"Performance improvement: {improvement:.1f}%")
        
        if improvement > 0:
            print(f"✅ Optimization successful! {improvement:.1f}% faster")
        else:
            print(f"❌ Optimization ineffective. {abs(improvement):.1f}% slower")
        
        print("\n📋 OUTCOME COMPARISON:")
        print(f"Original options: {len(original_outcome.options)}")
        print(f"Parallel options: {len(parallel_outcome.options)}")
        
        # Show sample outcomes
        if parallel_outcome.options:
            print(f"\nSample outcome: {parallel_outcome.options[0].title}")
            print(f"Description: {parallel_outcome.options[0].description}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your environment")


if __name__ == "__main__":
    asyncio.run(main())
