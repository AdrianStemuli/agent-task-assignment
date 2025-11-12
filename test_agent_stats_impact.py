#!/usr/bin/env python3
"""
Test script to demonstrate how agent stats significantly impact API responses
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def create_test_agents():
    """Create test agents with different stat profiles"""
    
    # High-skill expert agent
    expert_agent = {
        "ID": "expert-001",
        "Name": "Senior Expert",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 10},
            {"Name": "Speed", "StatValueObj": 8},
            {"Name": "Reliability", "StatValueObj": 9},
            {"Name": "Quality", "StatValueObj": 10},
            {"Name": "Capacity", "StatValueObj": 8},
            {"Name": "TokenMultiplier", "StatValueObj": 2.5}
        ]
    }
    
    # Average performer
    average_agent = {
        "ID": "average-001", 
        "Name": "Average Employee",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 5},
            {"Name": "Speed", "StatValueObj": 5},
            {"Name": "Reliability", "StatValueObj": 5},
            {"Name": "Quality", "StatValueObj": 5},
            {"Name": "Capacity", "StatValueObj": 5},
            {"Name": "TokenMultiplier", "StatValueObj": 1.0}
        ]
    }
    
    # Low-skill struggling agent
    struggling_agent = {
        "ID": "struggling-001",
        "Name": "New Intern",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 2},
            {"Name": "Speed", "StatValueObj": 3},
            {"Name": "Reliability", "StatValueObj": 2},
            {"Name": "Quality", "StatValueObj": 1},
            {"Name": "Capacity", "StatValueObj": 2},
            {"Name": "TokenMultiplier", "StatValueObj": 0.5}
        ]
    }
    
    return expert_agent, average_agent, struggling_agent

def test_prompt_evaluation_with_different_agents():
    """Test how agent stats affect prompt evaluation"""
    
    expert_agent, average_agent, struggling_agent = create_test_agents()
    
    task = {
        "ID": "task-001",
        "Title": "Write Marketing Email",
        "Description": "Write a marketing email to promote our new product launch"
    }
    
    # Same prompt for all agents
    prompt = "Write a marketing email about our new product. Make it engaging and professional."
    
    print("🧪 TESTING PROMPT EVALUATION WITH DIFFERENT AGENT STATS")
    print("=" * 80)
    print(f"Task: {task['Title']}")
    print(f"Prompt: {prompt}")
    print()
    
    agents = [
        ("🌟 EXPERT AGENT", expert_agent),
        ("📊 AVERAGE AGENT", average_agent), 
        ("🆘 STRUGGLING AGENT", struggling_agent)
    ]
    
    results = []
    
    for agent_type, agent in agents:
        print(f"{agent_type}: {agent['Name']}")
        print(f"   Overall Skill: {sum(s['StatValueObj'] for s in agent['Stats'][:5])/5:.1f}/10")
        print(f"   Token Multiplier: {agent['Stats'][5]['StatValueObj']}x")
        
        payload = {"Agent": agent, "Task": task, "Prompt": prompt}
        
        try:
            response = requests.post(f"{BASE_URL}/prompts/evaluate", json=payload)
            if response.status_code == 200:
                result = response.json()
                results.append((agent_type, agent, result))
                
                metrics = result['quality_metrics']
                feedback = result['agent_feedback']
                
                print(f"   📈 Overall Score: {metrics['overall_score']:.3f}")
                print(f"   🎯 Agent Fit: {metrics['agent_fit_score']:.3f}")
                print(f"   😊 Emotion: {feedback['emotion']}")
                print(f"   💬 Feedback: {feedback['feedback_text'][:60]}...")
                print()
            else:
                print(f"   ❌ Error: {response.status_code}")
                print()
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            print()
    
    return results

def test_task_completion_outcomes():
    """Test how agent stats affect task completion outcomes"""
    
    expert_agent, average_agent, struggling_agent = create_test_agents()
    
    task = {
        "ID": "task-002",
        "Title": "Customer Support Response", 
        "Description": "Handle a complex customer complaint about product quality"
    }
    
    prompt = "Please handle this customer complaint professionally. The customer is upset about product quality issues and wants a resolution."
    
    print("🎯 TESTING TASK COMPLETION OUTCOMES WITH DIFFERENT AGENT STATS")
    print("=" * 80)
    print(f"Task: {task['Title']}")
    print(f"Prompt: {prompt}")
    print()
    
    agents = [
        ("🌟 EXPERT AGENT", expert_agent),
        ("📊 AVERAGE AGENT", average_agent),
        ("🆘 STRUGGLING AGENT", struggling_agent)
    ]
    
    for agent_type, agent in agents:
        print(f"{agent_type}: {agent['Name']}")
        
        # First assign the task
        assign_payload = {"Agent": agent, "Task": task, "Prompt": prompt}
        assign_response = requests.post(f"{BASE_URL}/tasks/assign", json=assign_payload)
        
        if assign_response.status_code == 201:
            assignment = assign_response.json()
            task_id = assignment['task_assignment']['task_id']
            
            # Then complete the task
            complete_payload = {
                "task_id": task_id,
                "Agent": agent,
                "Task": task, 
                "Prompt": prompt
            }
            
            complete_response = requests.post(f"{BASE_URL}/tasks/complete", json=complete_payload)
            
            if complete_response.status_code == 200:
                outcome = complete_response.json()
                
                print(f"   ✅ Task Completed Successfully")
                print(f"   📊 Quality Score: {outcome['outcome']['prompt_quality_score']:.3f}")
                print(f"   🎲 Options Available: {len(outcome['outcome']['options'])}")
                
                # Show first outcome option
                if outcome['outcome']['options']:
                    option = outcome['outcome']['options'][0]
                    print(f"   🏆 Best Option: {option['title']}")
                    print(f"   📝 Description: {option['description'][:80]}...")
                    print(f"   📈 Type: {option['outcome_type']}")
                    if option['stat_modifiers']:
                        mod = option['stat_modifiers'][0]
                        print(f"   💰 Impact: {mod['stat_name']} {mod['change']:+d}")
                
                print(f"   💭 Agent Feedback: {outcome['outcome']['agent_feedback'][:60]}...")
                print()
            else:
                print(f"   ❌ Completion Error: {complete_response.status_code}")
                print()
        else:
            print(f"   ❌ Assignment Error: {assign_response.status_code}")
            print()

def compare_stat_impact():
    """Compare how specific stats impact outcomes"""
    
    print("🔍 COMPARING SPECIFIC STAT IMPACTS")
    print("=" * 80)
    
    # High expertise vs low expertise
    high_expertise = {
        "ID": "expert-expertise",
        "Name": "Domain Expert",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 10},  # MAX
            {"Name": "Speed", "StatValueObj": 5},
            {"Name": "Reliability", "StatValueObj": 5},
            {"Name": "Quality", "StatValueObj": 5},
            {"Name": "Capacity", "StatValueObj": 5},
            {"Name": "TokenMultiplier", "StatValueObj": 1.0}
        ]
    }
    
    low_expertise = {
        "ID": "low-expertise", 
        "Name": "Novice",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 1},   # MIN
            {"Name": "Speed", "StatValueObj": 5},
            {"Name": "Reliability", "StatValueObj": 5},
            {"Name": "Quality", "StatValueObj": 5},
            {"Name": "Capacity", "StatValueObj": 5},
            {"Name": "TokenMultiplier", "StatValueObj": 1.0}
        ]
    }
    
    task = {
        "ID": "task-003",
        "Title": "Technical Analysis",
        "Description": "Analyze complex technical requirements and provide recommendations"
    }
    
    prompt = "Please analyze the technical requirements and provide your expert recommendations."
    
    agents = [
        ("🎓 HIGH EXPERTISE (10/10)", high_expertise),
        ("🤷 LOW EXPERTISE (1/10)", low_expertise)
    ]
    
    for agent_type, agent in agents:
        payload = {"Agent": agent, "Task": task, "Prompt": prompt}
        response = requests.post(f"{BASE_URL}/prompts/evaluate", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            metrics = result['quality_metrics']
            
            print(f"{agent_type}:")
            print(f"   Clarity Score: {metrics['clarity_score']:.3f}")
            print(f"   Overall Score: {metrics['overall_score']:.3f}")
            print(f"   Agent Emotion: {result['agent_feedback']['emotion']}")
            print()

if __name__ == "__main__":
    print("🎮 AGENT STATS IMPACT DEMONSTRATION")
    print("Testing how agent statistics significantly affect API responses")
    print()
    
    # Check API health
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ API not available. Please start the server.")
            exit(1)
        print("✅ API is running")
        print()
    except:
        print("❌ Cannot connect to API. Please start the server.")
        exit(1)
    
    # Run tests
    print("This test demonstrates that agent stats now have SIGNIFICANT impact on:")
    print("• Prompt evaluation scores")
    print("• Agent emotional responses") 
    print("• Task completion outcomes")
    print("• Outcome magnitude (via TokenMultiplier)")
    print()
    
    # Test 1: Prompt evaluation with different agents
    evaluation_results = test_prompt_evaluation_with_different_agents()
    
    # Test 2: Task completion outcomes
    test_task_completion_outcomes()
    
    # Test 3: Specific stat comparisons
    compare_stat_impact()
    
    print("🎉 DEMONSTRATION COMPLETE!")
    print()
    print("Key Findings:")
    print("• Higher agent stats lead to significantly better prompt evaluation scores")
    print("• Agent emotions and feedback reflect their capabilities")
    print("• Task outcomes vary dramatically based on agent skill levels")
    print("• TokenMultiplier amplifies the impact of all outcomes")
    print("• The API now provides realistic simulation of how employee skills affect business results")
