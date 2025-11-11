"""
Service for evaluating prompt quality and generating feedback
"""

from typing import Dict, List, Tuple
from models.agent import Agent
from models.task import Task
from models.prompt import Prompt, PromptParameterType
from models.responses import PromptQualityMetrics, AgentFeedbackResponse
from .openai_service import OpenAIService
import json


class PromptEvaluator:
    """Service for evaluating prompt quality"""
    
    def __init__(self, openai_service: OpenAIService):
        """
        Initialize prompt evaluator
        
        Args:
            openai_service: OpenAI service instance
        """
        self.openai_service = openai_service
    
    def calculate_base_scores(self, prompt: Prompt, agent: Agent, task: Task) -> Dict[str, float]:
        """
        Calculate base scores from prompt parameters and text analysis
        
        Args:
            prompt: The prompt to evaluate
            agent: The agent who will receive the prompt
            task: The task context
            
        Returns:
            Dictionary of base scores
        """
        # Get parameter values (default to 5 if not specified)
        clarity_param = prompt.get_parameter_value("Clarity") / 10.0
        context_param = prompt.get_parameter_value("Context") / 10.0
        tone_param = prompt.get_parameter_value("Tone") / 10.0
        agency_param = prompt.get_parameter_value("Agency") / 10.0
        empathy_param = prompt.get_parameter_value("Empathy") / 10.0
        
        # Analyze prompt text
        text_length = len(prompt.Text)
        word_count = len(prompt.Text.split())
        has_agent_name = agent.Name.lower() in prompt.Text.lower()
        has_task_reference = any(word in prompt.Text.lower() for word in task.Title.lower().split())
        
        # Calculate text-based modifiers
        length_modifier = min(1.0, text_length / 200)  # Longer prompts tend to have more context
        detail_modifier = min(1.0, word_count / 30)  # More words = more detail
        personalization_modifier = 1.2 if has_agent_name else 1.0
        relevance_modifier = 1.1 if has_task_reference else 1.0
        
        # Calculate individual scores
        clarity_score = clarity_param * detail_modifier
        context_score = context_param * length_modifier * relevance_modifier
        tone_score = tone_param * personalization_modifier
        agency_score = agency_param
        empathy_score = empathy_param * personalization_modifier
        
        # Calculate agent fit based on preferences
        agent_autonomy_pref = agent.autonomy_preference / 10.0
        agency_fit = 1.0 - abs(agency_param - agent_autonomy_pref)
        
        return {
            "clarity_score": min(1.0, clarity_score),
            "context_score": min(1.0, context_score),
            "tone_score": min(1.0, tone_score),
            "agency_score": min(1.0, agency_score),
            "empathy_score": min(1.0, empathy_score),
            "agent_fit_score": agency_fit
        }
    
    async def evaluate_prompt_with_ai(
        self,
        prompt: Prompt,
        agent: Agent,
        task: Task
    ) -> Tuple[PromptQualityMetrics, AgentFeedbackResponse, List[str]]:
        """
        Evaluate prompt quality using AI
        
        Args:
            prompt: The prompt to evaluate
            agent: The agent who will receive the prompt
            task: The task context
            
        Returns:
            Tuple of (quality metrics, agent feedback, suggestions)
        """
        # Calculate base scores
        base_scores = self.calculate_base_scores(prompt, agent, task)
        
        # Prepare context for AI evaluation
        system_prompt = """You are an expert in prompt engineering and workplace communication. 
Your job is to evaluate prompts given to employees for task assignments.
Evaluate the prompt based on:
1. Clarity - How clear and specific is the prompt?
2. Context - How much relevant context is provided?
3. Tone - Is the tone appropriate and motivating?
4. Agency - Does it balance direction with autonomy?
5. Empathy - Does it show understanding of the agent's perspective?

Respond with a JSON object containing:
- overall_score: float (0-1)
- agent_emotion: string (e.g., "motivated", "confused", "overwhelmed", "excited")
- agent_feedback: string (max 300 chars, from agent's perspective)
- visual_indicator: string (e.g., "thumbs_up", "question_mark", "star", "warning")
- suggestions: array of strings (2-4 specific suggestions for improvement)
- is_ready: boolean (whether prompt is good enough to proceed)
"""
        
        agent_stats_str = ", ".join([f"{stat.Name}: {stat.Value}" for stat in agent.Stats])
        
        user_prompt = f"""Evaluate this prompt:

AGENT PROFILE:
- Name: {agent.Name}
- Department: {agent.Department.value}
- Stats: {agent_stats_str}
- Autonomy Preference: {agent.autonomy_preference}/10
- Preferred Tone: {agent.preferred_tone}

TASK:
- Title: {task.Title}
- Description: {task.Description}

PROMPT TEXT:
"{prompt.Text}"

PROMPT PARAMETERS:
{json.dumps([{"Name": p.Name.value, "Value": p.Value} for p in prompt.Parameters], indent=2)}

BASE SCORES (for reference):
{json.dumps(base_scores, indent=2)}

Provide your evaluation as JSON."""
        
        try:
            ai_response = await self.openai_service.generate_json_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7
            )
            
            # Combine base scores with AI evaluation
            overall_score = ai_response.get("overall_score", sum(base_scores.values()) / len(base_scores))
            
            quality_metrics = PromptQualityMetrics(
                overall_score=overall_score,
                clarity_score=base_scores["clarity_score"],
                context_score=base_scores["context_score"],
                tone_score=base_scores["tone_score"],
                agency_score=base_scores["agency_score"],
                empathy_score=base_scores["empathy_score"],
                agent_fit_score=base_scores["agent_fit_score"]
            )
            
            agent_feedback = AgentFeedbackResponse(
                emotion=ai_response.get("agent_emotion", "neutral"),
                feedback_text=ai_response.get("agent_feedback", "I understand the task."),
                visual_indicator=ai_response.get("visual_indicator", "neutral")
            )
            
            suggestions = ai_response.get("suggestions", [])
            
            return quality_metrics, agent_feedback, suggestions
            
        except Exception as e:
            # Fallback to base scores if AI fails
            print(f"AI evaluation failed, using base scores: {e}")
            print(f"Base scores: {base_scores}")
            overall_score = sum(base_scores.values()) / len(base_scores)
            
            quality_metrics = PromptQualityMetrics(
                overall_score=overall_score,
                **base_scores
            )
            
            # Generate simple feedback based on score
            if overall_score >= 0.8:
                emotion = "motivated"
                feedback = "This looks great! I have a clear understanding of what's needed."
                indicator = "thumbs_up"
            elif overall_score >= 0.6:
                emotion = "ready"
                feedback = "Good prompt. I can work with this."
                indicator = "check"
            elif overall_score >= 0.4:
                emotion = "uncertain"
                feedback = "I think I understand, but could use more clarity."
                indicator = "question_mark"
            else:
                emotion = "confused"
                feedback = "I'm not sure what you want me to do here."
                indicator = "warning"
            
            agent_feedback = AgentFeedbackResponse(
                emotion=emotion,
                feedback_text=feedback,
                visual_indicator=indicator
            )
            
            suggestions = self._generate_fallback_suggestions(prompt, base_scores)
            
            return quality_metrics, agent_feedback, suggestions
    
    def _generate_fallback_suggestions(self, prompt: Prompt, scores: Dict[str, float]) -> List[str]:
        """Generate fallback suggestions based on scores"""
        suggestions = []
        
        if scores["clarity_score"] < 0.6:
            suggestions.append("Add more specific details about what you want accomplished")
        
        if scores["context_score"] < 0.6:
            suggestions.append("Provide more context about why this task is important")
        
        if scores["tone_score"] < 0.6:
            suggestions.append("Consider using a more encouraging and collaborative tone")
        
        if scores["empathy_score"] < 0.6:
            suggestions.append("Show understanding of the agent's perspective and constraints")
        
        if not suggestions:
            suggestions.append("Your prompt looks good! Consider adding more specific examples if needed.")
        
        return suggestions[:4]  # Return max 4 suggestions
    
    async def suggest_refinements(
        self,
        prompt: Prompt,
        agent: Agent,
        task: Task,
        focus_parameter: str = None
    ) -> Tuple[str, Dict[str, str], float]:
        """
        Suggest refinements to improve the prompt
        
        Args:
            prompt: The current prompt
            agent: The agent who will receive the prompt
            task: The task context
            focus_parameter: Optional specific parameter to focus on
            
        Returns:
            Tuple of (refined_prompt_text, improvements_dict, expected_improvement)
        """
        system_prompt = """You are an expert in prompt engineering. 
Your job is to refine prompts to make them more effective for task assignments.
Provide a refined version that improves the specified aspects while maintaining the core intent.

Respond with a JSON object containing:
- refined_text: string (the improved prompt)
- improvements: object (map of parameter names to what was improved)
- expected_improvement: float (0-1, how much better the refined prompt should be)
"""
        
        focus_text = f"\nFOCUS ON: {focus_parameter}" if focus_parameter else ""
        
        user_prompt = f"""Refine this prompt:

AGENT: {agent.Name} ({agent.Department.value})
TASK: {task.Title}

CURRENT PROMPT:
"{prompt.Text}"

CURRENT PARAMETERS:
{json.dumps([{"Name": p.Name.value, "Value": p.Value} for p in prompt.Parameters], indent=2)}
{focus_text}

Provide a refined version that improves clarity, context, tone, agency, and empathy."""
        
        try:
            ai_response = await self.openai_service.generate_json_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7
            )
            
            refined_text = ai_response.get("refined_text", prompt.Text)
            improvements = ai_response.get("improvements", {})
            expected_improvement = ai_response.get("expected_improvement", 0.2)
            
            return refined_text, improvements, expected_improvement
            
        except Exception as e:
            # Fallback refinement
            refined_text = self._generate_fallback_refinement(prompt, agent, task, focus_parameter)
            improvements = {"General": "Added more detail and context"}
            expected_improvement = 0.15
            
            return refined_text, improvements, expected_improvement
    
    def _generate_fallback_refinement(
        self,
        prompt: Prompt,
        agent: Agent,
        task: Task,
        focus_parameter: str = None
    ) -> str:
        """Generate a simple fallback refinement"""
        base_text = prompt.Text
        
        # Add agent name if missing
        if agent.Name.lower() not in base_text.lower():
            base_text = f"Hey {agent.Name}! {base_text}"
        
        # Add more context
        if len(base_text.split()) < 20:
            base_text += f" This is for our {agent.Department.value} department and relates to {task.Title}."
        
        return base_text
