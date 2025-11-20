"""
Ultra-optimized service for generating task outcomes with maximum parallelization
"""

import asyncio
from typing import List, Dict, Any, Tuple, Optional
import uuid
import json
from concurrent.futures import ThreadPoolExecutor
from models.agent import Agent
from models.task import Task
from models.prompt import Prompt
from models.outcome import TaskOutcome, OutcomeOption, OutcomeType, StatModifier
from .openai_service import OpenAIService


class UltraParallelOutcomeGenerator:
    """Ultra-optimized service with maximum parallelization and caching"""
    
    def __init__(self, openai_service: OpenAIService):
        """
        Initialize ultra-parallel outcome generator
        
        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self._prompt_cache = {}  # Simple in-memory cache
        self._agent_analysis_cache = {}
    
    async def generate_outcomes(
        self,
        task_id: str,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> TaskOutcome:
        """
        Generate task outcomes using ultra-parallel approach
        
        Args:
            task_id: ID of the task
            agent: The agent who completed the task
            task: The completed task
            prompt: The prompt that was used
            quality_score: Quality score of the prompt (0-1)
            
        Returns:
            TaskOutcome with multiple options
        """
        # Pre-calculate common data
        num_options = self._determine_num_options(quality_score)
        outcome_distribution = self._determine_outcome_distribution(quality_score)
        
        # Create cache key for agent analysis
        agent_cache_key = f"{agent.Name}_{agent.get_overall_skill_level()}"
        if agent_cache_key not in self._agent_analysis_cache:
            self._agent_analysis_cache[agent_cache_key] = self._calculate_agent_modifiers(agent)
        agent_modifiers = self._agent_analysis_cache[agent_cache_key]
        
        # Create multiple parallel tasks with different strategies
        tasks_to_run = [
            # Core outcome generation
            self._generate_primary_outcomes(agent, task, prompt, quality_score, num_options, outcome_distribution, agent_modifiers),
            
            # Alternative outcome generation (different temperature)
            self._generate_alternative_outcomes(agent, task, prompt, quality_score, num_options),
            
            # Agent feedback and emotional response
            self._generate_comprehensive_feedback(agent, task, prompt, quality_score),
            
            # Narrative and context generation
            self._generate_rich_narrative(agent, task, prompt, quality_score),
            
            # Performance metrics and insights
            self._generate_performance_insights(agent, task, prompt, quality_score)
        ]
        
        try:
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks_to_run, return_exceptions=True)
            
            # Process results and handle any exceptions
            primary_outcomes = results[0] if not isinstance(results[0], Exception) else None
            alternative_outcomes = results[1] if not isinstance(results[1], Exception) else None
            feedback_data = results[2] if not isinstance(results[2], Exception) else None
            narrative_data = results[3] if not isinstance(results[3], Exception) else None
            insights_data = results[4] if not isinstance(results[4], Exception) else None
            
            # Combine and optimize results
            final_options = self._combine_outcome_options(
                primary_outcomes, alternative_outcomes, num_options
            )
            
            # Enhanced feedback with insights
            agent_feedback = self._combine_feedback(feedback_data, insights_data, quality_score)
            
            # Enhance options with narrative context
            if narrative_data:
                self._enhance_options_with_narrative(final_options, narrative_data)
            
            # Ensure minimum options
            if len(final_options) < 2:
                final_options.extend(self._generate_fallback_options(agent, task, quality_score, 2 - len(final_options)))
            
            return TaskOutcome(
                task_id=task_id,
                agent_name=agent.Name,
                prompt_quality_score=quality_score,
                options=final_options[:4],  # Max 4 options
                agent_feedback=agent_feedback
            )
            
        except Exception as e:
            # Fallback to simple generation
            return self._generate_fallback_outcome(task_id, agent, task, quality_score)
    
    async def _generate_primary_outcomes(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float,
        num_options: int,
        outcome_distribution: str,
        agent_modifiers: str
    ) -> Dict[str, Any]:
        """Generate primary outcome options"""
        
        system_prompt = """You are a game designer creating primary outcome options for a business simulation.
Focus on realistic, engaging outcomes that reflect both prompt quality and agent capabilities.

Respond with JSON containing:
- options: array of {title, description, outcome_type, stat_modifiers: [{stat_name, change, percentage}], narrative_text}
"""
        
        agent_stats_str = ", ".join([f"{stat.Name}: {stat.StatValueObj}" for stat in agent.Stats])
        
        user_prompt = f"""Generate {num_options} primary outcomes:

AGENT: {agent.Name} ({agent.Department.value}) - Skill: {agent.get_overall_skill_level():.1f}/10
TASK: {task.Title} - {task.Description[:100]}...
PROMPT QUALITY: {quality_score:.2f}/1.0
DISTRIBUTION: {outcome_distribution}

Focus on outcomes that showcase the agent's capabilities and the impact of prompt quality."""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=1000
        )
    
    async def _generate_alternative_outcomes(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float,
        num_options: int
    ) -> Dict[str, Any]:
        """Generate alternative outcome options with different creativity"""
        
        system_prompt = """You are a creative game designer generating alternative outcome scenarios.
Think outside the box while maintaining realism. Focus on unexpected but plausible results.

Respond with JSON containing:
- options: array of {title, description, outcome_type, stat_modifiers, narrative_text}
"""
        
        user_prompt = f"""Generate {min(2, num_options)} creative alternative outcomes:

AGENT: {agent.Name} - {agent.Department.value}
TASK: {task.Title}
QUALITY: {quality_score:.2f}

What unexpected but realistic outcomes could occur?"""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.9,  # Higher creativity
            max_tokens=800
        )
    
    async def _generate_comprehensive_feedback(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> Dict[str, Any]:
        """Generate comprehensive agent feedback"""
        
        system_prompt = """You are simulating an employee's detailed reflection on a completed task.
Provide authentic, nuanced feedback that reflects the agent's personality and experience level.

Respond with JSON containing:
- feedback: string (detailed agent reflection)
- emotion: string (primary emotion)
- confidence: float (0-1)
- satisfaction: float (0-1)
- learning_points: array of strings
- suggestions_for_future: array of strings
"""
        
        user_prompt = f"""Generate comprehensive feedback from {agent.Name}'s perspective:

AGENT PROFILE:
- Name: {agent.Name} ({agent.Department.value})
- Skill Level: {agent.get_overall_skill_level():.1f}/10
- Autonomy Preference: {agent.autonomy_preference}/10
- Preferred Tone: {agent.preferred_tone}

TASK: {task.Title}
PROMPT: "{prompt.Text[:200]}..."
QUALITY SCORE: {quality_score:.2f}/1.0

How does this specific agent feel about this experience?"""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=600
        )
    
    async def _generate_rich_narrative(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> Dict[str, Any]:
        """Generate rich narrative context"""
        
        system_prompt = """You are a storyteller creating engaging narratives for business simulation outcomes.
Focus on the human elements: what the agent was thinking, challenges faced, breakthroughs achieved.

Respond with JSON containing:
- execution_story: string (detailed story of task execution)
- key_moments: array of strings (critical moments during execution)
- challenges_faced: array of strings
- successes_achieved: array of strings
- impact_on_team: string
"""
        
        user_prompt = f"""Create a rich narrative for this task execution:

AGENT: {agent.Name} (Skill: {agent.get_overall_skill_level():.1f}/10)
TASK: {task.Title}
PROMPT QUALITY: {quality_score:.2f}/1.0

Tell the story of how this agent approached and completed this task."""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=700
        )
    
    async def _generate_performance_insights(
        self,
        agent: Agent,
        task: Task,
        prompt: Prompt,
        quality_score: float
    ) -> Dict[str, Any]:
        """Generate performance insights and analytics"""
        
        system_prompt = """You are a performance analyst providing insights on task completion effectiveness.
Focus on measurable impacts and learning opportunities.

Respond with JSON containing:
- efficiency_rating: float (0-1)
- innovation_level: float (0-1)
- collaboration_impact: float (0-1)
- skill_development: array of strings
- process_improvements: array of strings
- business_impact: string
"""
        
        user_prompt = f"""Analyze the performance of this task completion:

AGENT CAPABILITIES:
- Expertise: {agent.get_stat_value('Expertise')}/10
- Quality: {agent.get_stat_value('Quality')}/10
- Reliability: {agent.get_stat_value('Reliability')}/10

TASK: {task.Title}
PROMPT QUALITY: {quality_score:.2f}/1.0

What insights can we derive about performance and impact?"""
        
        return await self.openai_service.generate_json_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.6,
            max_tokens=500
        )
    
    def _combine_outcome_options(
        self,
        primary_outcomes: Optional[Dict[str, Any]],
        alternative_outcomes: Optional[Dict[str, Any]],
        num_options: int
    ) -> List[OutcomeOption]:
        """Combine and optimize outcome options from different sources"""
        all_options = []
        
        # Add primary outcomes
        if primary_outcomes and "options" in primary_outcomes:
            for option_data in primary_outcomes["options"][:num_options]:
                try:
                    option = self._create_outcome_option(option_data)
                    all_options.append(option)
                except Exception:
                    continue
        
        # Add alternative outcomes if we need more
        if alternative_outcomes and "options" in alternative_outcomes and len(all_options) < num_options:
            needed = num_options - len(all_options)
            for option_data in alternative_outcomes["options"][:needed]:
                try:
                    option = self._create_outcome_option(option_data)
                    all_options.append(option)
                except Exception:
                    continue
        
        return all_options
    
    def _create_outcome_option(self, option_data: Dict[str, Any]) -> OutcomeOption:
        """Create an OutcomeOption from data"""
        stat_modifiers = [
            StatModifier(**mod) for mod in option_data.get("stat_modifiers", [])
        ]
        
        return OutcomeOption(
            option_id=f"outcome_{uuid.uuid4().hex[:8]}",
            title=option_data.get("title", "Task Result"),
            description=option_data.get("description", "Task completed."),
            outcome_type=OutcomeType(option_data.get("outcome_type", "neutral")),
            stat_modifiers=stat_modifiers,
            narrative_text=option_data.get("narrative_text", "The task was completed.")
        )
    
    def _combine_feedback(
        self,
        feedback_data: Optional[Dict[str, Any]],
        insights_data: Optional[Dict[str, Any]],
        quality_score: float
    ) -> str:
        """Combine feedback from different sources"""
        if feedback_data and "feedback" in feedback_data:
            base_feedback = feedback_data["feedback"]
            
            # Add insights if available
            if insights_data and "business_impact" in insights_data:
                base_feedback += f" {insights_data['business_impact']}"
            
            return base_feedback
        
        # Fallback feedback
        return self._generate_feedback_based_on_quality(quality_score)
    
    def _enhance_options_with_narrative(
        self,
        options: List[OutcomeOption],
        narrative_data: Dict[str, Any]
    ):
        """Enhance options with rich narrative context"""
        if not narrative_data or not options:
            return
        
        execution_story = narrative_data.get("execution_story", "")
        key_moments = narrative_data.get("key_moments", [])
        
        for i, option in enumerate(options):
            if i < len(key_moments) and len(option.narrative_text) < 150:
                # Enhance with specific key moment
                option.narrative_text = f"{key_moments[i]} {option.narrative_text}"
            elif execution_story and len(option.narrative_text) < 100:
                # Enhance with general execution context
                story_snippet = execution_story[:100] + "..."
                option.narrative_text = f"{story_snippet} {option.narrative_text}"
    
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
        """Calculate and describe agent capability modifiers (cached)"""
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
        
        return f"Expertise: {expertise}/10 ({get_level_desc(expertise)}), Quality: {quality}/10 ({get_level_desc(quality)}), Reliability: {reliability}/10 ({get_level_desc(reliability)}), Speed: {speed}/10 ({get_level_desc(speed)}), Capacity: {capacity}/10 ({get_level_desc(capacity)}), Multiplier: {token_multiplier:.1f}x"
