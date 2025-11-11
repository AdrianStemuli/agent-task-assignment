"""
Service for generating task outcomes based on prompt quality
"""

from typing import List
import uuid
from models.agent import Agent
from models.task import Task
from models.prompt import Prompt
from models.outcome import TaskOutcome, OutcomeOption, OutcomeType, StatModifier
from .openai_service import OpenAIService
import json


class OutcomeGenerator:
    """Service for generating task outcomes"""
    
    def __init__(self, openai_service: OpenAIService):
        """
        Initialize outcome generator
        
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
        Generate task outcomes based on prompt quality
        
        Args:
            task_id: ID of the task
            agent: The agent who completed the task
            task: The completed task
            prompt: The prompt that was used
            quality_score: Quality score of the prompt (0-1)
            
        Returns:
            TaskOutcome with multiple options
        """
        # Determine outcome distribution based on quality
        num_options = self._determine_num_options(quality_score)
        outcome_distribution = self._determine_outcome_distribution(quality_score)
        
        system_prompt = """You are a game designer creating outcomes for a business simulation game.
Generate realistic and engaging outcomes for completed tasks based on the prompt quality.

For HIGH quality prompts (0.8+):
- Generate mostly positive outcomes (buffs) with significant stat improvements
- Include creative and impactful results
- Show how clear communication leads to excellent work

For MEDIUM quality prompts (0.5-0.8):
- Generate mixed outcomes (some buffs, some neutral, maybe minor debuffs)
- Show decent results but with room for improvement
- Reflect that adequate communication leads to adequate results

For LOW quality prompts (below 0.5):
- Generate mostly negative outcomes (debuffs) or minimal benefits
- Show how poor communication leads to suboptimal work
- Include consequences like wasted resources, low morale, or missed opportunities

Each outcome should:
1. Be specific to the task and department
2. Include 1-3 stat modifiers (e.g., Revenue, Morale, Productivity, Customer Satisfaction, Brand Awareness, etc.)
3. Have engaging narrative text explaining what happened
4. Feel realistic and educational

Respond with a JSON object containing:
- options: array of outcome options (2-4 options)
  - title: string (short catchy title)
  - description: string (what the agent produced)
  - outcome_type: "buff", "debuff", or "neutral"
  - stat_modifiers: array of {stat_name, change, percentage}
  - narrative_text: string (story of what happened)
- agent_feedback: string (agent's reflection on the task and prompt quality)
"""
        
        agent_stats_str = ", ".join([f"{stat.Name}: {stat.Value}" for stat in agent.Stats])
        
        user_prompt = f"""Generate {num_options} outcome options for this completed task:

AGENT:
- Name: {agent.Name}
- Department: {agent.Department.value}
- Stats: {agent_stats_str}
- Overall Skill: {agent.get_overall_skill_level():.1f}/10

TASK:
- Title: {task.Title}
- Description: {task.Description}

PROMPT USED:
"{prompt.Text}"

PROMPT QUALITY SCORE: {quality_score:.2f}/1.0

OUTCOME DISTRIBUTION GUIDANCE:
{json.dumps(outcome_distribution, indent=2)}

Generate {num_options} distinct outcome options that reflect the prompt quality.
Better prompts = better outcomes. Worse prompts = worse outcomes.
Make the outcomes feel like natural consequences of the communication quality."""
        
        try:
            ai_response = await self.openai_service.generate_json_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,
                max_tokens=2000
            )
            
            # Parse options
            options = []
            for idx, option_data in enumerate(ai_response.get("options", [])):
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
            
            agent_feedback = ai_response.get(
                "agent_feedback",
                self._generate_feedback_based_on_quality(quality_score)
            )
            
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
            # Fallback to generated outcomes
            return self._generate_fallback_outcome(task_id, agent, task, quality_score)
    
    def _determine_num_options(self, quality_score: float) -> int:
        """Determine number of outcome options based on quality"""
        if quality_score >= 0.8:
            return 3  # High quality = more good options
        elif quality_score >= 0.5:
            return 3  # Medium quality = mixed options
        else:
            return 2  # Low quality = fewer options (mostly bad)
    
    def _determine_outcome_distribution(self, quality_score: float) -> dict:
        """Determine the distribution of outcome types based on quality"""
        if quality_score >= 0.8:
            return {
                "buffs": 3,
                "neutral": 0,
                "debuffs": 0,
                "description": "All positive outcomes with significant benefits"
            }
        elif quality_score >= 0.7:
            return {
                "buffs": 2,
                "neutral": 1,
                "debuffs": 0,
                "description": "Mostly positive with one neutral option"
            }
        elif quality_score >= 0.5:
            return {
                "buffs": 1,
                "neutral": 1,
                "debuffs": 1,
                "description": "Mixed outcomes reflecting adequate communication"
            }
        elif quality_score >= 0.3:
            return {
                "buffs": 0,
                "neutral": 1,
                "debuffs": 2,
                "description": "Mostly negative with minimal benefits"
            }
        else:
            return {
                "buffs": 0,
                "neutral": 0,
                "debuffs": 2,
                "description": "All negative outcomes due to poor communication"
            }
    
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
            # Good outcome
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
            # Neutral outcome
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
            # Poor outcome
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
