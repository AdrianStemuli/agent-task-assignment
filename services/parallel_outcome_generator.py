"""
Optimized service for generating task outcomes using parallel OpenAI calls
"""

import asyncio
from typing import List, Dict, Any, Tuple
import uuid
from models.agent import Agent
from models.task import Task
from models.prompt import Prompt
from models.outcome import TaskOutcome, OutcomeOption, OutcomeType, StatModifier
from .openai_service import OpenAIService
import json


class ParallelOutcomeGenerator:
    """Optimized service for generating task outcomes using parallel OpenAI calls"""
    
    def __init__(self, openai_service: OpenAIService):
        """
        Initialize parallel outcome generator
        
        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service
    
    async def generate_outcomes(
        self,
        task_id: str,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> TaskOutcome:
        """
        Generate task outcomes using parallel OpenAI calls for faster response
        
        Args:
            task_id: ID of the task
            agent: The agent who completed the task
            task: The completed task
            prompt: The prompt that was used
            quality_score: Quality score of the prompt (0-1)
            
        Returns:
            TaskOutcome with multiple options
        """
        # Determine outcome parameters
        num_options = self._determine_num_options(quality_score)
        outcome_distribution = self._determine_outcome_distribution(quality_score)
        agent_modifiers = self._calculate_agent_modifiers(agent)
        
        # Create parallel tasks for different components
        tasks_to_run = [
            self._generate_outcome_options(agent, task, prompt, quality_score, num_options, outcome_distribution, agent_modifiers),
            self._generate_agent_feedback(agent, task, prompt, quality_score),
            self._generate_narrative_context(agent, task, prompt, quality_score)
        ]
        
        try:
            # Run all tasks in parallel
            options_result, feedback_result, narrative_context = await asyncio.gather(*tasks_to_run)
            
            # Parse and combine results
            options = self._parse_outcome_options(options_result, num_options)
            agent_feedback = feedback_result.get("feedback", self._generate_feedback_based_on_quality(quality_score))
            
            # Enhance options with narrative context if available
            if narrative_context and len(options) > 0:
                self._enhance_options_with_context(options, narrative_context)
            
            # Ensure we have at least 2 options
            if len(options) < 2:
                options.extend(self._generate_fallback_options(agent, task, quality_score, 2 - len(options)))
            
            return TaskOutcome(
                task_id=task_id,
                agent_name=agent.Name,
                prompt_quality_score=quality_score,
                options=options[:4],  # Max 4 options
                agent_feedback=agent_feedback
            )
            
        except Exception as e:
            # Fallback to simple generation
            return self._generate_fallback_outcome(task_id, agent, task, quality_score)
    
    async def _generate_outcome_options(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float,
        num_options: int,
        outcome_distribution: str,
        agent_modifiers: str
    ) -> Dict[str, Any]:
        """Generate outcome options in parallel"""
        
        system_prompt = """You are a game designer creating outcome options for a business simulation game.
Generate realistic outcome options based on prompt quality and agent capabilities.

Focus on:
1. Creating diverse options (buff/neutral/debuff based on quality)
2. Making outcomes specific to the task and department
3. Reflecting agent capabilities in the results
4. Including appropriate stat modifiers

Respond with JSON containing:
- options: array of {title, description, outcome_type, stat_modifiers: [{stat_name, change, percentage}]}
"""
        
        agent_stats_str = ", ".join([f"{stat.Name}: {stat.StatValueObj}" for stat in agent.Stats])
        
        user_prompt = f"""Generate {num_options} outcome options:

AGENT: {agent.Name} ({agent.Department.value})
STATS: {agent_stats_str}
SKILL LEVEL: {agent.get_overall_skill_level():.1f}/10
TOKEN MULTIPLIER: {agent.get_token_multiplier():.1f}x

TASK: {task.Title}
DESCRIPTION: {task.Description}

PROMPT: "{prompt.Text}"
QUALITY SCORE: {quality_score:.2f}/1.0

DISTRIBUTION: {outcome_distribution}

Generate options that reflect both prompt quality and agent capabilities."""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=1200
        )
    
    async def _generate_agent_feedback(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> Dict[str, Any]:
        """Generate agent feedback in parallel"""
        
        system_prompt = """You are simulating an employee's reflection on a completed task.
Generate realistic feedback from the agent's perspective about the task and prompt quality.

Respond with JSON containing:
- feedback: string (agent's reflection on the experience, max 300 chars)
- emotion: string (how the agent feels about the task)
- confidence: float (0-1, how confident the agent is in their work)
"""
        
        user_prompt = f"""Generate feedback from {agent.Name}'s perspective:

AGENT: {agent.Name} ({agent.Department.value})
AUTONOMY PREFERENCE: {agent.autonomy_preference}/10
PREFERRED TONE: {agent.preferred_tone}

TASK: {task.Title}
PROMPT: "{prompt.Text}"
QUALITY SCORE: {quality_score:.2f}/1.0

How does this agent feel about the task and prompt quality?"""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=400
        )
    
    async def _generate_narrative_context(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> Dict[str, Any]:
        """Generate narrative context for outcomes in parallel"""
        
        system_prompt = """You are a storyteller creating engaging narratives for business simulation outcomes.
Generate context about what happened during task execution based on agent capabilities and prompt quality.

Respond with JSON containing:
- execution_story: string (what happened during execution)
- key_factors: array of strings (what influenced the outcome)
- lessons_learned: string (what can be learned from this)
"""
        
        user_prompt = f"""Generate narrative context:

AGENT: {agent.Name} with {agent.get_overall_skill_level():.1f}/10 skill level
TASK: {task.Title}
PROMPT QUALITY: {quality_score:.2f}/1.0

What story explains how this agent approached and completed this task?"""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=600
        )
    
    def _parse_outcome_options(self, options_result: Dict[str, Any], num_options: int) -> List[OutcomeOption]:
        """Parse outcome options from AI response"""
        options = []
        
        for idx, option_data in enumerate(options_result.get("options", [])[:num_options]):
            try:
                stat_modifiers = [
                    StatModifier(**mod) for mod in option_data.get("stat_modifiers", [])
                ]
                
                option = OutcomeOption(
                    option_id=f"outcome_{uuid.uuid4().hex[:8]}",
                    title=option_data.get("title", f"Option {idx + 1}"),
                    description=option_data.get("description", "Task completed."),
                    outcome_type=OutcomeType(option_data.get("outcome_type", "neutral")),
                    stat_modifiers=stat_modifiers,
                    narrative_text=option_data.get("narrative_text", "The task was completed.")
                )
                options.append(option)
            except Exception:
                # Skip malformed options
                continue
        
        return options
    
    def _enhance_options_with_context(self, options: List[OutcomeOption], narrative_context: Dict[str, Any]):
        """Enhance options with narrative context"""
        execution_story = narrative_context.get("execution_story", "")
        
        for option in options:
            if execution_story and len(option.narrative_text) < 100:
                # Enhance short narratives with execution context
                option.narrative_text = f"{execution_story} {option.narrative_text}"
    
    def _determine_num_options(self, quality_score: float) -> int:
        """Determine number of outcome options based on quality"""
        if quality_score >= 0.8:
            return 3
        else:
            return 2
    
    def _determine_outcome_distribution(self, quality_score: float) -> str:
        """Determine the distribution of outcome types based on quality"""
        if quality_score >= 0.8:
            return "80% positive, 20% neutral"
        elif quality_score >= 0.6:
            return "40% positive, 40% neutral, 20% negative"
        elif quality_score >= 0.4:
            return "20% positive, 30% neutral, 50% negative"
        else:
            return "10% positive, 20% neutral, 70% negative"
    
    def _generate_feedback_based_on_quality(self, quality_score: float) -> str:
        """Generate agent feedback based on quality score"""
        if quality_score >= 0.8:
            return "Excellent prompt! The clear direction and context really helped me deliver my best work."
        elif quality_score >= 0.7:
            return "Good prompt! I had a clear understanding of what was needed and could work effectively."
        elif quality_score >= 0.5:
            return "The prompt was okay. I completed the task, but more clarity would have helped me do better."
        elif quality_score >= 0.3:
            return "The prompt was a bit unclear. I did my best, but I wasn't sure if this is what you wanted."
        else:
            return "I struggled with this prompt. More specific direction would really help me understand your expectations."
    
    def _generate_fallback_options(
        self,
        agent: Agent,
        task: Task,
        quality_score: float,
        num_options: int
    ) -> List[OutcomeOption]:
        """Generate fallback outcome options"""
        options = []
        
        if quality_score >= 0.7:
            options.append(OutcomeOption(
                option_id=f"outcome_{uuid.uuid4().hex[:8]}",
                title=f"Successful {task.Title}",
                description=f"{agent.Name} completed the task with good results.",
                outcome_type=OutcomeType.BUFF,
                stat_modifiers=[
                    StatModifier(stat_name="Productivity", change=10, percentage=True),
                    StatModifier(stat_name="Morale", change=5, percentage=True)
                ],
                narrative_text="The clear communication led to effective execution."
            ))
        
        if quality_score < 0.7 and quality_score >= 0.4:
            options.append(OutcomeOption(
                option_id=f"outcome_{uuid.uuid4().hex[:8]}",
                title=f"Adequate {task.Title}",
                description=f"{agent.Name} completed the task with acceptable results.",
                outcome_type=OutcomeType.NEUTRAL,
                stat_modifiers=[
                    StatModifier(stat_name="Productivity", change=2, percentage=True)
                ],
                narrative_text="The task was completed, though there's room for improvement."
            ))
        
        if quality_score < 0.5:
            options.append(OutcomeOption(
                option_id=f"outcome_{uuid.uuid4().hex[:8]}",
                title=f"Suboptimal {task.Title}",
                description=f"{agent.Name} struggled with unclear direction.",
                outcome_type=OutcomeType.DEBUFF,
                stat_modifiers=[
                    StatModifier(stat_name="Morale", change=-5, percentage=True),
                    StatModifier(stat_name="Efficiency", change=-8, percentage=True)
                ],
                narrative_text="Unclear communication led to wasted effort and frustration."
            ))
        
        return options[:num_options]
    
    def _generate_fallback_outcome(
        self,
        task_id: str,
        agent: Agent,
        task: Task,
        quality_score: float
    ) -> TaskOutcome:
        """Generate a complete fallback outcome"""
        num_options = self._determine_num_options(quality_score)
        options = self._generate_fallback_options(agent, task, quality_score, num_options)
        
        return TaskOutcome(
            task_id=task_id,
            agent_name=agent.Name,
            prompt_quality_score=quality_score,
            options=options,
            agent_feedback=self._generate_feedback_based_on_quality(quality_score)
        )
    
    def _calculate_agent_modifiers(self, agent: Agent) -> str:
        """Calculate and describe agent capability modifiers"""
        expertise = agent.get_stat_value("Expertise")
        quality = agent.get_stat_value("Quality") 
        reliability = agent.get_stat_value("Reliability")
        speed = agent.get_stat_value("Speed")
        capacity = agent.get_stat_value("Capacity")
        token_multiplier = agent.get_token_multiplier()
        
        def get_level_desc(value: float) -> str:
            if value >= 8: return "EXCELLENT"
            elif value >= 6: return "GOOD" 
            elif value >= 4: return "AVERAGE"
            elif value >= 2: return "POOR"
            else: return "VERY POOR"
        
        analysis = f"""Expertise: {expertise}/10 ({get_level_desc(expertise)}), Quality: {quality}/10 ({get_level_desc(quality)}), Reliability: {reliability}/10 ({get_level_desc(reliability)}), Speed: {speed}/10 ({get_level_desc(speed)}), Capacity: {capacity}/10 ({get_level_desc(capacity)}), Multiplier: {token_multiplier:.1f}x"""
        
        return analysis
