"""
Prompt Generator Service

Generates base prompts for different types of tasks to help users get started
with effective task assignments.
"""

import json
from typing import Dict, List, Optional
from models.task import Task, TaskCategory
from models.agent import Agent
from services.openai_service import OpenAIService


class PromptGenerator:
    """Service for generating base prompts for tasks"""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        
        # Template prompts for different task categories
        self.prompt_templates = {
            TaskCategory.EMAIL_CAMPAIGN: [
                "Please write a professional email campaign for {task_description}. Include a compelling subject line, clear value proposition, and strong call-to-action.",
                "Create an engaging email marketing campaign about {task_description}. Focus on customer benefits and include personalization elements.",
                "Draft a persuasive email campaign for {task_description}. Use a conversational tone and highlight key benefits for the target audience."
            ],
            TaskCategory.SOCIAL_MEDIA: [
                "Create engaging social media content for {task_description}. Include relevant hashtags and a call-to-action that encourages engagement.",
                "Develop a social media post about {task_description}. Make it shareable, visually descriptive, and aligned with our brand voice.",
                "Write compelling social media content for {task_description}. Focus on storytelling and community engagement."
            ],
            TaskCategory.MARKET_RESEARCH: [
                "Conduct thorough market research on {task_description}. Analyze competitors, target demographics, and market trends. Provide actionable insights.",
                "Research and analyze {task_description}. Include market size, key players, opportunities, and potential challenges.",
                "Perform comprehensive market analysis for {task_description}. Focus on data-driven insights and strategic recommendations."
            ],
            TaskCategory.WORKSHOP: [
                "Design and plan a workshop on {task_description}. Include learning objectives, activities, timeline, and materials needed.",
                "Create a comprehensive workshop plan for {task_description}. Focus on interactive elements and practical takeaways.",
                "Develop an engaging workshop curriculum for {task_description}. Include hands-on exercises and assessment methods."
            ],
            TaskCategory.TRAINING: [
                "Develop a training program for {task_description}. Include learning objectives, modules, assessments, and success metrics.",
                "Create comprehensive training materials for {task_description}. Focus on practical skills and real-world applications.",
                "Design an effective training curriculum for {task_description}. Include interactive elements and progress tracking."
            ],
            TaskCategory.RECRUITMENT: [
                "Create a recruitment strategy for {task_description}. Include job requirements, sourcing channels, and evaluation criteria.",
                "Develop a comprehensive hiring plan for {task_description}. Focus on attracting top talent and efficient screening processes.",
                "Design a recruitment process for {task_description}. Include job descriptions, interview questions, and selection criteria."
            ],
            TaskCategory.PRODUCT_RESEARCH: [
                "Conduct detailed product research on {task_description}. Analyze features, user feedback, market positioning, and improvement opportunities.",
                "Research and evaluate {task_description}. Include competitive analysis, user needs assessment, and feature recommendations.",
                "Perform comprehensive product analysis for {task_description}. Focus on market fit, user experience, and growth potential."
            ],
            TaskCategory.COMPETITIVE_ANALYSIS: [
                "Analyze competitors for {task_description}. Include strengths, weaknesses, market positioning, and strategic recommendations.",
                "Conduct thorough competitive analysis of {task_description}. Focus on differentiation opportunities and market gaps.",
                "Research and compare competitors in {task_description}. Provide actionable insights for competitive advantage."
            ],
            TaskCategory.USER_STUDY: [
                "Design and conduct a user study for {task_description}. Include research methodology, participant criteria, and analysis framework.",
                "Plan a comprehensive user research study on {task_description}. Focus on user behavior, needs, and pain points.",
                "Create a user study protocol for {task_description}. Include data collection methods and success metrics."
            ],
            TaskCategory.FEATURE_DEVELOPMENT: [
                "Develop the feature for {task_description}. Include technical specifications, implementation plan, and testing strategy.",
                "Create a comprehensive development plan for {task_description}. Focus on user requirements, technical architecture, and quality assurance.",
                "Design and implement {task_description}. Include code structure, documentation, and deployment considerations."
            ],
            TaskCategory.BUG_FIX: [
                "Investigate and fix the bug related to {task_description}. Include root cause analysis, solution implementation, and testing procedures.",
                "Debug and resolve the issue with {task_description}. Focus on thorough testing and prevention of similar issues.",
                "Analyze and fix the problem in {task_description}. Include code review, testing, and documentation updates."
            ],
            TaskCategory.CODE_REVIEW: [
                "Conduct a thorough code review for {task_description}. Focus on code quality, security, performance, and best practices.",
                "Review and analyze the code for {task_description}. Provide constructive feedback and improvement suggestions.",
                "Perform comprehensive code review of {task_description}. Include security analysis, performance optimization, and maintainability."
            ],
            TaskCategory.UI_DESIGN: [
                "Design the user interface for {task_description}. Focus on usability, accessibility, and visual appeal.",
                "Create UI mockups and prototypes for {task_description}. Include user flow, wireframes, and design specifications.",
                "Develop user interface designs for {task_description}. Focus on user experience and brand consistency."
            ],
            TaskCategory.UX_RESEARCH: [
                "Conduct UX research for {task_description}. Include user interviews, usability testing, and behavior analysis.",
                "Research user experience aspects of {task_description}. Focus on user needs, pain points, and improvement opportunities.",
                "Perform comprehensive UX analysis for {task_description}. Include user journey mapping and interaction design."
            ],
            TaskCategory.PROTOTYPE: [
                "Create a prototype for {task_description}. Include interactive elements, user flows, and testing scenarios.",
                "Develop a working prototype of {task_description}. Focus on core functionality and user validation.",
                "Build and test a prototype for {task_description}. Include user feedback collection and iteration planning."
            ],
            TaskCategory.SALES_PITCH: [
                "Prepare a compelling sales pitch for {task_description}. Include value proposition, benefits, and call-to-action.",
                "Create a persuasive sales presentation about {task_description}. Focus on customer needs and solution benefits.",
                "Develop a sales strategy for {task_description}. Include market positioning, competitive advantages, and closing techniques."
            ],
            TaskCategory.CLIENT_MEETING: [
                "Prepare for the client meeting about {task_description}. Include agenda, key points, and expected outcomes.",
                "Plan and conduct a client meeting for {task_description}. Focus on relationship building and value delivery.",
                "Organize a productive client discussion on {task_description}. Include preparation materials and follow-up actions."
            ],
            TaskCategory.PROPOSAL: [
                "Write a comprehensive proposal for {task_description}. Include scope, timeline, budget, and deliverables.",
                "Create a detailed project proposal for {task_description}. Focus on client needs, solution approach, and value proposition.",
                "Develop a winning proposal for {task_description}. Include competitive analysis, risk mitigation, and success metrics."
            ],
            TaskCategory.PROCESS_OPTIMIZATION: [
                "Analyze and optimize the process for {task_description}. Include current state analysis, improvement recommendations, and implementation plan.",
                "Improve operational efficiency for {task_description}. Focus on bottleneck identification and workflow optimization.",
                "Streamline and enhance the process of {task_description}. Include automation opportunities and performance metrics."
            ],
            TaskCategory.RESOURCE_PLANNING: [
                "Create a resource plan for {task_description}. Include capacity analysis, allocation strategy, and timeline coordination.",
                "Develop resource allocation strategy for {task_description}. Focus on optimal utilization and project success.",
                "Plan and manage resources for {task_description}. Include skill requirements, availability, and budget considerations."
            ],
            TaskCategory.REPORTING: [
                "Generate a comprehensive report on {task_description}. Include data analysis, insights, and actionable recommendations.",
                "Create detailed reporting for {task_description}. Focus on key metrics, trends, and strategic implications.",
                "Prepare analytical report about {task_description}. Include visualizations, conclusions, and next steps."
            ],
            TaskCategory.CUSTOM: [
                "Please complete the task: {task_description}. Provide a thorough and professional approach with clear deliverables.",
                "Work on {task_description}. Focus on quality, attention to detail, and meeting all requirements.",
                "Handle {task_description} with care and professionalism. Ensure all aspects are covered comprehensively."
            ]
        }
    
    async def generate_base_prompt(
        self, 
        task: Task, 
        agent: Optional[Agent] = None,
        style_preference: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate a base prompt for a given task
        
        Args:
            task: The task to generate a prompt for
            agent: Optional agent to customize the prompt for
            style_preference: Optional style preference (professional, casual, detailed, concise)
        
        Returns:
            Dictionary containing generated prompts and metadata
        """
        
        # Get template prompts for the task category
        templates = self.prompt_templates.get(task.Category, self.prompt_templates[TaskCategory.CUSTOM])
        
        # Format templates with task description
        base_prompts = []
        for template in templates:
            formatted_prompt = template.format(task_description=task.Description)
            base_prompts.append(formatted_prompt)
        
        # If OpenAI is available and agent is provided, generate AI-enhanced prompts
        ai_enhanced_prompts = []
        if self.openai_service and agent:
            try:
                ai_enhanced_prompts = await self._generate_ai_enhanced_prompts(task, agent, style_preference)
            except Exception as e:
                print(f"AI enhancement failed: {e}")
                # Continue with template prompts if AI fails
        
        # Combine template and AI-generated prompts
        all_prompts = base_prompts + ai_enhanced_prompts
        
        # Remove duplicates while preserving order
        unique_prompts = []
        seen = set()
        for prompt in all_prompts:
            if prompt not in seen:
                unique_prompts.append(prompt)
                seen.add(prompt)
        
        return {
            "task_id": task.ID,
            "task_title": task.Title,
            "task_category": task.Category.value,
            "generated_prompts": unique_prompts[:5],  # Limit to 5 prompts
            "prompt_count": len(unique_prompts[:5]),
            "style_applied": style_preference or "default",
            "agent_customized": agent is not None,
            "generation_method": "template_and_ai" if ai_enhanced_prompts else "template_only"
        }
    
    async def _generate_ai_enhanced_prompts(
        self, 
        task: Task, 
        agent: Agent, 
        style_preference: Optional[str]
    ) -> List[str]:
        """Generate AI-enhanced prompts using OpenAI"""
        
        agent_stats_str = ", ".join([f"{stat.Name}: {stat.StatValueObj}" for stat in agent.Stats])
        style_text = f"\nStyle preference: {style_preference}" if style_preference else ""
        
        system_prompt = """You are an expert prompt engineer. Generate effective task prompts that are:
- Clear and specific
- Action-oriented
- Appropriate for the agent's skill level
- Optimized for the requested style
- Professional yet engaging

Return 2-3 different prompt variations as a JSON array of strings."""

        user_prompt = f"""Generate effective prompts for this task assignment:

TASK:
- Title: {task.Title}
- Description: {task.Description}
- Category: {task.Category.value}

AGENT PROFILE:
- Name: {agent.Name}
- Department: {agent.Department.value}
- Stats: {agent_stats_str}
- Skill Level: {agent.get_overall_skill_level():.1f}/10{style_text}

Generate 2-3 different prompt variations that would be effective for this agent and task."""

        try:
            response = await self.openai_service.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            # Try to parse as JSON array
            import json
            try:
                prompts = json.loads(response)
                if isinstance(prompts, list):
                    return [str(prompt) for prompt in prompts if prompt]
            except json.JSONDecodeError:
                # If not JSON, split by lines and clean up
                lines = response.strip().split('\n')
                prompts = []
                for line in lines:
                    line = line.strip()
                    # Remove numbering, quotes, and bullet points
                    line = line.lstrip('123456789.- "\'`')
                    line = line.rstrip('"\'`')
                    if line and len(line) > 20:  # Only include substantial prompts
                        prompts.append(line)
                return prompts[:3]  # Limit to 3
                
        except Exception as e:
            print(f"AI prompt generation failed: {e}")
            return []
        
        return []
    
    def get_prompt_suggestions_by_category(self, category: TaskCategory) -> List[str]:
        """Get template prompt suggestions for a specific category"""
        templates = self.prompt_templates.get(category, self.prompt_templates[TaskCategory.CUSTOM])
        return [template.replace("{task_description}", "[task description]") for template in templates]
    
    def get_all_categories_with_examples(self) -> Dict[str, List[str]]:
        """Get all task categories with example prompts"""
        result = {}
        for category, templates in self.prompt_templates.items():
            result[category.value] = [
                template.replace("{task_description}", "[task description]") 
                for template in templates
            ]
        return result
