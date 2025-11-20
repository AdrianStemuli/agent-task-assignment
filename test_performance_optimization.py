"""
Comprehensive performance testing and optimization suite
"""

import asyncio
import time
import json
import statistics
from typing import List, Dict, Any
import uuid
from concurrent.futures import ThreadPoolExecutor

from services.openai_service import OpenAIService
from services.parallel_outcome_generator import ParallelOutcomeGenerator
from services.outcome_generator import OutcomeGenerator
from services.prompt_evaluator import PromptEvaluator
from models.agent import Agent, AgentStat, Department
from models.task import Task, TaskStatus, TaskCategory
from models.prompt import Prompt, PromptParameter, PromptParameterType
from config import settings


class PerformanceTestSuite:
    """Comprehensive performance testing suite"""
    
    def __init__(self):
        self.openai_service = None
        self.prompt_evaluator = None
        self.outcome_generator = None
        self.parallel_outcome_generator = None
        self.test_results = []
    
    async def initialize(self):
        """Initialize all services"""
        try:
            self.openai_service = OpenAIService()
            self.prompt_evaluator = PromptEvaluator(self.openai_service)
            self.outcome_generator = OutcomeGenerator(self.openai_service)
            self.parallel_outcome_generator = ParallelOutcomeGenerator(self.openai_service)
            print("✅ All services initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            raise
    
    def create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Create various test scenarios with different complexities"""
        scenarios = []
        
        # Scenario 1: Simple task, high-skill agent
        scenarios.append({
            "name": "Simple Task - High Skill Agent",
            "agent": Agent(
                ID=str(uuid.uuid4()),
                Name="Senior Analyst",
                Department=Department.RESEARCH,
                Stats=[
                    AgentStat(Name="Expertise", StatValueObj=9),
                    AgentStat(Name="Quality", StatValueObj=8),
                    AgentStat(Name="Reliability", StatValueObj=9),
                    AgentStat(Name="Speed", StatValueObj=7),
                    AgentStat(Name="Capacity", StatValueObj=8),
                ],
                autonomy_preference=8,
                preferred_tone="professional"
            ),
            "task": Task(
                ID=str(uuid.uuid4()),
                Title="Email Summary",
                Description="Summarize daily emails for management",
                status=TaskStatus.IN_PROGRESS,
                category=TaskCategory.EMAIL_CAMPAIGN
            ),
            "prompt": Prompt(
                Text="Please review today's emails and create a brief summary for the management team.",
                Parameters=[
                    PromptParameter(Name=PromptParameterType.CLARITY, Value=8),
                    PromptParameter(Name=PromptParameterType.TONE, Value=8),
                    PromptParameter(Name=PromptParameterType.AGENCY, Value=7),
                    PromptParameter(Name=PromptParameterType.EMPATHY, Value=6),
                ]
            )
        })
        
        # Scenario 2: Complex task, medium-skill agent
        scenarios.append({
            "name": "Complex Task - Medium Skill Agent",
            "agent": Agent(
                ID=str(uuid.uuid4()),
                Name="Marketing Coordinator",
                Department=Department.MARKETING,
                Stats=[
                    AgentStat(Name="Expertise", StatValueObj=5),
                    AgentStat(Name="Quality", StatValueObj=6),
                    AgentStat(Name="Reliability", StatValueObj=5),
                    AgentStat(Name="Speed", StatValueObj=6),
                    AgentStat(Name="Capacity", StatValueObj=4),
                ],
                autonomy_preference=5,
                preferred_tone="collaborative"
            ),
            "task": Task(
                ID=str(uuid.uuid4()),
                Title="Market Analysis Report",
                Description="Conduct comprehensive market analysis for Q4 strategy planning including competitor analysis, trend identification, and strategic recommendations",
                status=TaskStatus.IN_PROGRESS,
                category=TaskCategory.MARKET_RESEARCH
            ),
            "prompt": Prompt(
                Text="I need you to conduct a thorough market analysis for our Q4 planning. Please analyze our competitors, identify key market trends, assess our position, and provide strategic recommendations. Include data visualization suggestions and consider both short-term and long-term implications.",
                Parameters=[
                    PromptParameter(Name=PromptParameterType.CLARITY, Value=6),
                    PromptParameter(Name=PromptParameterType.TONE, Value=7),
                    PromptParameter(Name=PromptParameterType.AGENCY, Value=5),
                    PromptParameter(Name=PromptParameterType.EMPATHY, Value=7),
                ]
            )
        })
        
        # Scenario 3: Simple task, low-skill agent
        scenarios.append({
            "name": "Simple Task - Low Skill Agent",
            "agent": Agent(
                ID=str(uuid.uuid4()),
                Name="Junior Assistant",
                Department=Department.OPERATIONS,
                Stats=[
                    AgentStat(Name="Expertise", StatValueObj=2),
                    AgentStat(Name="Quality", StatValueObj=3),
                    AgentStat(Name="Reliability", StatValueObj=4),
                    AgentStat(Name="Speed", StatValueObj=3),
                    AgentStat(Name="Capacity", StatValueObj=2),
                ],
                autonomy_preference=3,
                preferred_tone="supportive"
            ),
            "task": Task(
                ID=str(uuid.uuid4()),
                Title="File Organization",
                Description="Organize project files in shared drive",
                status=TaskStatus.IN_PROGRESS,
                category=TaskCategory.UI_DESIGN
            ),
            "prompt": Prompt(
                Text="Please organize the project files in our shared drive according to the naming convention.",
                Parameters=[
                    PromptParameter(Name=PromptParameterType.CLARITY, Value=9),
                    PromptParameter(Name=PromptParameterType.TONE, Value=9),
                    PromptParameter(Name=PromptParameterType.AGENCY, Value=4),
                    PromptParameter(Name=PromptParameterType.EMPATHY, Value=8),
                ]
            )
        })
        
        return scenarios
    
    async def test_original_approach(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test original sequential approach"""
        agent = scenario["agent"]
        task = scenario["task"]
        prompt = scenario["prompt"]
        
        start_time = time.time()
        
        # Sequential execution
        quality_metrics, _, _ = await self.prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task
        )
        
        outcome = await self.outcome_generator.generate_outcomes(
            task_id=task.ID,
            agent=agent,
            task=task,
            prompt=prompt,
            quality_score=quality_metrics.overall_score
        )
        
        duration = time.time() - start_time
        
        return {
            "approach": "original",
            "duration": duration,
            "quality_score": quality_metrics.overall_score,
            "options_count": len(outcome.options),
            "scenario": scenario["name"]
        }
    
    async def test_parallel_approach(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test parallel approach"""
        agent = scenario["agent"]
        task = scenario["task"]
        prompt = scenario["prompt"]
        
        start_time = time.time()
        
        # Parallel execution
        evaluation_task = self.prompt_evaluator.evaluate_prompt_with_ai(
            prompt=prompt,
            agent=agent,
            task=task
        )
        
        base_quality_score = self.prompt_evaluator.calculate_base_scores(prompt, agent, task)
        estimated_quality = sum(base_quality_score.values()) / len(base_quality_score)
        
        outcome_task = self.parallel_outcome_generator.generate_outcomes(
            task_id=task.ID,
            agent=agent,
            task=task,
            prompt=prompt,
            quality_score=estimated_quality
        )
        
        (quality_metrics, _, _), outcome = await asyncio.gather(evaluation_task, outcome_task)
        outcome.prompt_quality_score = quality_metrics.overall_score
        
        duration = time.time() - start_time
        
        return {
            "approach": "parallel",
            "duration": duration,
            "quality_score": quality_metrics.overall_score,
            "options_count": len(outcome.options),
            "scenario": scenario["name"]
        }
    
    async def test_ultra_parallel_approach(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test ultra-parallel approach with even more concurrency"""
        agent = scenario["agent"]
        task = scenario["task"]
        prompt = scenario["prompt"]
        
        start_time = time.time()
        
        # Create multiple parallel tasks for different aspects
        tasks_to_run = []
        
        # 1. Prompt evaluation
        tasks_to_run.append(self.prompt_evaluator.evaluate_prompt_with_ai(prompt, agent, task))
        
        # 2. Base quality calculation (synchronous, but we can prepare it)
        base_quality_score = self.prompt_evaluator.calculate_base_scores(prompt, agent, task)
        estimated_quality = sum(base_quality_score.values()) / len(base_quality_score)
        
        # 3. Multiple outcome generation calls with different focuses
        tasks_to_run.append(self.parallel_outcome_generator._generate_outcome_options(
            agent, task, prompt, estimated_quality, 3, "mixed outcomes", "agent analysis"
        ))
        
        tasks_to_run.append(self.parallel_outcome_generator._generate_agent_feedback(
            agent, task, prompt, estimated_quality
        ))
        
        tasks_to_run.append(self.parallel_outcome_generator._generate_narrative_context(
            agent, task, prompt, estimated_quality
        ))
        
        # Run all in parallel
        results = await asyncio.gather(*tasks_to_run)
        
        # Combine results
        quality_metrics, _, _ = results[0]
        options_result = results[1]
        feedback_result = results[2]
        narrative_context = results[3]
        
        # Parse options
        options = self.parallel_outcome_generator._parse_outcome_options(options_result, 3)
        
        # Create final outcome
        from models.outcome import TaskOutcome
        outcome = TaskOutcome(
            task_id=task.ID,
            agent_name=agent.Name,
            prompt_quality_score=quality_metrics.overall_score,
            options=options,
            agent_feedback=feedback_result.get("feedback", "Task completed")
        )
        
        duration = time.time() - start_time
        
        return {
            "approach": "ultra_parallel",
            "duration": duration,
            "quality_score": quality_metrics.overall_score,
            "options_count": len(outcome.options),
            "scenario": scenario["name"]
        }
    
    async def run_performance_tests(self, iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        print(f"🚀 Starting performance tests with {iterations} iterations per scenario...")
        
        scenarios = self.create_test_scenarios()
        all_results = []
        
        for scenario in scenarios:
            print(f"\n📊 Testing scenario: {scenario['name']}")
            scenario_results = []
            
            for i in range(iterations):
                print(f"  Iteration {i+1}/{iterations}")
                
                # Test all approaches
                original_result = await self.test_original_approach(scenario)
                parallel_result = await self.test_parallel_approach(scenario)
                ultra_parallel_result = await self.test_ultra_parallel_approach(scenario)
                
                scenario_results.extend([original_result, parallel_result, ultra_parallel_result])
                
                # Small delay between iterations
                await asyncio.sleep(0.5)
            
            all_results.extend(scenario_results)
        
        return self.analyze_results(all_results)
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance test results"""
        analysis = {
            "summary": {},
            "by_approach": {},
            "by_scenario": {},
            "recommendations": []
        }
        
        # Group results by approach
        by_approach = {}
        for result in results:
            approach = result["approach"]
            if approach not in by_approach:
                by_approach[approach] = []
            by_approach[approach].append(result)
        
        # Calculate statistics for each approach
        for approach, approach_results in by_approach.items():
            durations = [r["duration"] for r in approach_results]
            quality_scores = [r["quality_score"] for r in approach_results]
            
            analysis["by_approach"][approach] = {
                "avg_duration": statistics.mean(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                "avg_quality": statistics.mean(quality_scores),
                "total_tests": len(approach_results)
            }
        
        # Calculate improvements
        if "original" in analysis["by_approach"] and "parallel" in analysis["by_approach"]:
            original_avg = analysis["by_approach"]["original"]["avg_duration"]
            parallel_avg = analysis["by_approach"]["parallel"]["avg_duration"]
            improvement = ((original_avg - parallel_avg) / original_avg) * 100
            analysis["summary"]["parallel_improvement"] = improvement
        
        if "original" in analysis["by_approach"] and "ultra_parallel" in analysis["by_approach"]:
            original_avg = analysis["by_approach"]["original"]["avg_duration"]
            ultra_avg = analysis["by_approach"]["ultra_parallel"]["avg_duration"]
            ultra_improvement = ((original_avg - ultra_avg) / original_avg) * 100
            analysis["summary"]["ultra_parallel_improvement"] = ultra_improvement
        
        # Generate recommendations
        best_approach = min(analysis["by_approach"].items(), key=lambda x: x[1]["avg_duration"])
        analysis["recommendations"].append(f"Best performing approach: {best_approach[0]} ({best_approach[1]['avg_duration']:.2f}s avg)")
        
        if analysis["summary"].get("parallel_improvement", 0) > 20:
            analysis["recommendations"].append("Parallel approach shows significant improvement (>20%)")
        
        if analysis["summary"].get("ultra_parallel_improvement", 0) > analysis["summary"].get("parallel_improvement", 0):
            analysis["recommendations"].append("Ultra-parallel approach recommended for maximum performance")
        
        return analysis
    
    def print_results(self, analysis: Dict[str, Any]):
        """Print formatted results"""
        print("\n" + "="*80)
        print("📈 PERFORMANCE TEST RESULTS")
        print("="*80)
        
        print("\n🎯 SUMMARY:")
        for key, value in analysis["summary"].items():
            print(f"  {key}: {value:.1f}%")
        
        print("\n📊 BY APPROACH:")
        for approach, stats in analysis["by_approach"].items():
            print(f"\n  {approach.upper()}:")
            print(f"    Average Duration: {stats['avg_duration']:.3f}s")
            print(f"    Min/Max Duration: {stats['min_duration']:.3f}s / {stats['max_duration']:.3f}s")
            print(f"    Standard Deviation: {stats['std_duration']:.3f}s")
            print(f"    Average Quality: {stats['avg_quality']:.3f}")
            print(f"    Total Tests: {stats['total_tests']}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in analysis["recommendations"]:
            print(f"  • {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main test execution"""
    test_suite = PerformanceTestSuite()
    
    try:
        await test_suite.initialize()
        results = await test_suite.run_performance_tests(iterations=2)  # Reduced for faster testing
        test_suite.print_results(results)
        
        # Save detailed results
        with open("performance_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print("\n💾 Detailed results saved to 'performance_test_results.json'")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
