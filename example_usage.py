"""
Example usage script for Agent Task Assignment System
Demonstrates the complete workflow
"""

import asyncio
import json
from models import Agent, AgentStat, Department, Task, Prompt, PromptParameter, PromptParameterType
from models.requests import TaskAssignmentRequest, PromptEvaluationRequest, PromptRefinementRequest, TaskCompletionRequest
from services import OpenAIService, PromptEvaluator, OutcomeGenerator
from core import TaskManager


async def main():
    """Run example workflow"""
    
    print("=" * 60)
    print("Agent Task Assignment System - Example Usage")
    print("=" * 60)
    
    # Initialize services
    try:
        openai_service = OpenAIService()
        prompt_evaluator = PromptEvaluator(openai_service)
        outcome_generator = OutcomeGenerator(openai_service)
        task_manager = TaskManager()
        print("✓ Services initialized\n")
    except ValueError as e:
        print(f"⚠ Error: {e}")
        print("Please set OPENAI_API_KEY environment variable to run this example.\n")
        return
    
    # Create an agent
    agent = Agent(
        Name="Bob",
        Department=Department.RESEARCH,
        Stats=[
            AgentStat(Name="Expertise", Value=5),
            AgentStat(Name="Quality", Value=5),
            AgentStat(Name="Reliability", Value=6),
            AgentStat(Name="Speed", Value=3),
            AgentStat(Name="Capacity", Value=2)
        ],
        preferred_tone="empowering",
        autonomy_preference=7
    )
    
    # Create a task
    task = Task(
        Title="Write email campaign",
        Description="Write an email campaign that aims to increase customer retention by highlighting our new features"
    )
    
    # Create initial prompt (intentionally vague)
    initial_prompt = Prompt(
        Text="Write an email to customers",
        Parameters=[
            PromptParameter(Name=PromptParameterType.CLARITY, Value=3),
            PromptParameter(Name=PromptParameterType.CONTEXT, Value=2),
            PromptParameter(Name=PromptParameterType.TONE, Value=5),
            PromptParameter(Name=PromptParameterType.AGENCY, Value=5),
            PromptParameter(Name=PromptParameterType.EMPATHY, Value=4)
        ]
    )
    
    print(f"👤 Agent: {agent.Name} ({agent.Department.value})")
    print(f"📋 Task: {task.Title}")
    print(f"💬 Initial Prompt: \"{initial_prompt.Text}\"\n")
    
    # Step 1: Assign the task
    print("-" * 60)
    print("STEP 1: Assigning Task")
    print("-" * 60)
    
    assignment = task_manager.create_task_assignment(agent, task, initial_prompt)
    print(f"✓ Task assigned with ID: {assignment.task_id}")
    print(f"✓ Status: {assignment.status.value}\n")
    
    # Step 2: Evaluate initial prompt
    print("-" * 60)
    print("STEP 2: Evaluating Initial Prompt")
    print("-" * 60)
    
    quality_metrics, agent_feedback, suggestions = await prompt_evaluator.evaluate_prompt_with_ai(
        prompt=initial_prompt,
        agent=agent,
        task=task
    )
    
    print(f"📊 Quality Metrics:")
    print(f"   Overall Score: {quality_metrics.overall_score:.2f}")
    print(f"   Clarity: {quality_metrics.clarity_score:.2f}")
    print(f"   Context: {quality_metrics.context_score:.2f}")
    print(f"   Tone: {quality_metrics.tone_score:.2f}")
    print(f"   Agency: {quality_metrics.agency_score:.2f}")
    print(f"   Empathy: {quality_metrics.empathy_score:.2f}")
    print(f"   Agent Fit: {quality_metrics.agent_fit_score:.2f}")
    
    print(f"\n🎭 Agent Reaction:")
    print(f"   Emotion: {agent_feedback.emotion}")
    print(f"   Feedback: \"{agent_feedback.feedback_text}\"")
    print(f"   Visual: {agent_feedback.visual_indicator}")
    
    print(f"\n💡 Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # Step 3: Refine the prompt
    print("\n" + "-" * 60)
    print("STEP 3: Refining Prompt")
    print("-" * 60)
    
    refined_text, improvements, expected_improvement = await prompt_evaluator.suggest_refinements(
        prompt=initial_prompt,
        agent=agent,
        task=task,
        focus_parameter="Clarity"
    )
    
    print(f"✨ Refined Prompt:")
    print(f"   \"{refined_text}\"")
    
    print(f"\n📈 Improvements:")
    for param, improvement in improvements.items():
        print(f"   {param}: {improvement}")
    
    print(f"\n   Expected Quality Improvement: +{expected_improvement:.2f}")
    
    # Create refined prompt
    refined_prompt = Prompt(
        Text=refined_text,
        Parameters=[
            PromptParameter(Name=PromptParameterType.CLARITY, Value=8),
            PromptParameter(Name=PromptParameterType.CONTEXT, Value=7),
            PromptParameter(Name=PromptParameterType.TONE, Value=7),
            PromptParameter(Name=PromptParameterType.AGENCY, Value=7),
            PromptParameter(Name=PromptParameterType.EMPATHY, Value=6)
        ]
    )
    
    # Step 4: Re-evaluate refined prompt
    print("\n" + "-" * 60)
    print("STEP 4: Evaluating Refined Prompt")
    print("-" * 60)
    
    refined_quality_metrics, refined_agent_feedback, _ = await prompt_evaluator.evaluate_prompt_with_ai(
        prompt=refined_prompt,
        agent=agent,
        task=task
    )
    
    print(f"📊 New Quality Score: {refined_quality_metrics.overall_score:.2f} (was {quality_metrics.overall_score:.2f})")
    print(f"   Improvement: +{refined_quality_metrics.overall_score - quality_metrics.overall_score:.2f}")
    
    print(f"\n🎭 Agent Reaction:")
    print(f"   Emotion: {refined_agent_feedback.emotion}")
    print(f"   Feedback: \"{refined_agent_feedback.feedback_text}\"")
    
    # Step 5: Complete the task and generate outcomes
    print("\n" + "-" * 60)
    print("STEP 5: Completing Task & Generating Outcomes")
    print("-" * 60)
    
    outcome = await outcome_generator.generate_outcomes(
        task_id=assignment.task_id,
        agent=agent,
        task=task,
        prompt=refined_prompt,
        quality_score=refined_quality_metrics.overall_score
    )
    
    print(f"✅ Task Completed!")
    print(f"📊 Final Quality Score: {outcome.prompt_quality_score:.2f}")
    print(f"\n💬 Agent Feedback:")
    print(f"   \"{outcome.agent_feedback}\"")
    
    print(f"\n🎁 Outcome Options ({len(outcome.options)} available):")
    for i, option in enumerate(outcome.options, 1):
        print(f"\n   Option {i}: {option.title}")
        print(f"   Type: {option.outcome_type.value.upper()}")
        print(f"   Description: {option.description}")
        print(f"   Stat Modifiers:")
        for mod in option.stat_modifiers:
            sign = "+" if mod.change > 0 else ""
            unit = "%" if mod.percentage else ""
            print(f"      • {mod.stat_name}: {sign}{mod.change}{unit}")
        print(f"   Story: {option.narrative_text}")
    
    print("\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)
    print("\n📚 Key Takeaway:")
    print("Better prompts lead to better outcomes!")
    print(f"Initial score: {quality_metrics.overall_score:.2f} → Final score: {refined_quality_metrics.overall_score:.2f}")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
