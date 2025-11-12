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
        # Determine outcome distribution based on quality and agent stats
        num_options = self._determine_num_options(quality_score)
        outcome_distribution = self._determine_outcome_distribution(quality_score)
        
        # Calculate agent capability modifiers
        agent_modifiers = self._calculate_agent_modifiers(agent)
        
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
3. HEAVILY consider agent stats - outcomes should vary dramatically based on agent capabilities:
   - High Expertise (8-10): Generate innovative solutions, catch complex issues, provide deep insights
   - Low Expertise (1-3): Miss important details, make basic errors, need more guidance
   - High Quality (8-10): Deliver polished, professional results that exceed expectations
   - Low Quality (1-3): Produce work that needs significant revision or causes problems
   - High Reliability (8-10): Consistent delivery, builds trust, prevents issues
   - Low Reliability (1-3): Inconsistent results, creates uncertainty, may cause delays
   - High Speed (8-10): Fast turnaround, can handle urgent requests, increases efficiency
   - Low Speed (1-3): Slow delivery, may miss deadlines, reduces team velocity
   - High Capacity (8-10): Can handle complex/large tasks, multitask effectively
   - Low Capacity (1-3): Gets overwhelmed easily, needs simpler tasks, limited bandwidth
4. Scale outcome magnitude by TokenMultiplier (0.5x to 3.0x impact on stat changes)
5. Have engaging narrative text explaining what happened and WHY based on agent capabilities
6. Feel realistic and educational about how employee skills affect business outcomes

Respond with a JSON object containing:
- options: array of outcome options (2-4 options)
  - title: string (short catchy title)
  - description: string (what the agent produced)
  - outcome_type: "buff", "debuff", or "neutral"
  - stat_modifiers: array of {stat_name, change, percentage}
  - narrative_text: string (story of what happened)
- agent_feedback: string (agent's reflection on the task and prompt quality)
"""
        
        agent_stats_str = ", ".join([f"{stat.Name}: {stat.StatValueObj}" for stat in agent.Stats])
        
        user_prompt = f"""Generate {num_options} outcome options for this completed task:

AGENT:
- Name: {agent.Name}
- Department: {agent.Department.value}
- Stats: {agent_stats_str}
- Overall Skill: {agent.get_overall_skill_level():.1f}/10
- Token Multiplier: {agent.get_token_multiplier():.1f}x

TASK:
- Title: {task.Title}
- Description: {task.Description}

PROMPT USED:
"{prompt.Text}"

PROMPT QUALITY SCORE: {quality_score:.2f}/1.0

AGENT CAPABILITY ANALYSIS:
{agent_modifiers}

Expected outcome distribution: {outcome_distribution}

Generate outcomes that reflect both the prompt quality AND the agent's capabilities. Make the agent's stats significantly influence the results.
The outcomes should clearly show how this specific agent's strengths and weaknesses affected the task completion."""
        
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
            return 3  # Medium quality = mixed options
        else:
            return 2  # Low quality = fewer options (mostly bad)
    
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
        
        analysis = f"""- Expertise: {expertise}/10 ({get_level_desc(expertise)}) - Affects solution quality and innovation
- Quality: {quality}/10 ({get_level_desc(quality)}) - Affects output polish and professionalism  
- Reliability: {reliability}/10 ({get_level_desc(reliability)}) - Affects consistency and trust
- Speed: {speed}/10 ({get_level_desc(speed)}) - Affects delivery time and efficiency
- Capacity: {capacity}/10 ({get_level_desc(capacity)}) - Affects ability to handle complex tasks
- Token Multiplier: {token_multiplier:.1f}x - Amplifies all outcome impacts

EXPECTED PERFORMANCE: Agent will likely {'excel' if agent.get_overall_skill_level() >= 7 else 'struggle' if agent.get_overall_skill_level() <= 3 else 'perform adequately'} at this task."""
        
        return analysis
