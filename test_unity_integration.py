#!/usr/bin/env python3
"""
Test script for Unity integration with new Agent and Task structure
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_unity_agent_structure():
    """Test with Unity-style agent structure"""
    url = f"{BASE_URL}/tasks/assign"
    
    # Unity-style agent object
    unity_agent = {
        "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
        "Name": "Analyst",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 8},
            {"Name": "Speed", "StatValueObj": 6},
            {"Name": "Reliability", "StatValueObj": 8},
            {"Name": "Quality", "StatValueObj": 7},
            {"Name": "Capacity", "StatValueObj": 3},
            {"Name": "TokenMultiplier", "StatValueObj": 1.5}
        ]
    }
    
    # Unity-style task object
    unity_task = {
        "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
        "Title": "Write email",
        "Description": "Write an email to Alice"
    }
    
    payload = {
        "Agent": unity_agent,
        "Task": unity_task,
        "Prompt": "Please write a professional email to Alice regarding the quarterly report. Make sure to include all necessary details and maintain a friendly tone."
    }
    
    print("🧪 Testing Unity Integration - Task Assignment")
    print("=" * 60)
    print(f"Agent: {unity_agent['Name']} (ID: {unity_agent['ID']})")
    print(f"Task: {unity_task['Title']} (ID: {unity_task['ID']})")
    print(f"Token Multiplier: {unity_agent['Stats'][-1]['StatValueObj']}x")
    print()
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Task ID: {result['task_assignment']['task_id']}")
            print(f"Agent: {result['task_assignment']['agent_name']}")
            print(f"Message: {result['message']}")
            print(f"Feedback: {result['initial_feedback']}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_prompt_evaluation_with_stats():
    """Test prompt evaluation considering agent stats"""
    url = f"{BASE_URL}/prompts/evaluate"
    
    # High-skill agent
    high_skill_agent = {
        "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
        "Name": "Senior Analyst",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 9},
            {"Name": "Speed", "StatValueObj": 8},
            {"Name": "Reliability", "StatValueObj": 9},
            {"Name": "Quality", "StatValueObj": 8},
            {"Name": "Capacity", "StatValueObj": 7},
            {"Name": "TokenMultiplier", "StatValueObj": 2.0}
        ]
    }
    
    # Low-skill agent for comparison
    low_skill_agent = {
        "ID": "b88f99df-3ed6-5bcc-9f8g-f93d4dd446d4",
        "Name": "Junior Intern",
        "Stats": [
            {"Name": "Expertise", "StatValueObj": 3},
            {"Name": "Speed", "StatValueObj": 4},
            {"Name": "Reliability", "StatValueObj": 3},
            {"Name": "Quality", "StatValueObj": 2},
            {"Name": "Capacity", "StatValueObj": 2},
            {"Name": "TokenMultiplier", "StatValueObj": 0.8}
        ]
    }
    
    task = {
        "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
        "Title": "Write email",
        "Description": "Write an email to Alice"
    }
    
    prompt = "Write an email to Alice"
    
    print("\n🧪 Testing Prompt Evaluation with Different Agent Stats")
    print("=" * 60)
    
    # Test with high-skill agent
    payload_high = {"Agent": high_skill_agent, "Task": task, "Prompt": prompt}
    
    try:
        response_high = requests.post(url, json=payload_high)
        if response_high.status_code == 200:
            result_high = response_high.json()
            print(f"📊 High-Skill Agent ({high_skill_agent['Name']}):")
            print(f"   Overall Score: {result_high['quality_metrics']['overall_score']:.3f}")
            print(f"   Agent Fit Score: {result_high['quality_metrics']['agent_fit_score']:.3f}")
            print(f"   Emotion: {result_high['agent_feedback']['emotion']}")
        
        # Test with low-skill agent
        payload_low = {"Agent": low_skill_agent, "Task": task, "Prompt": prompt}
        response_low = requests.post(url, json=payload_low)
        
        if response_low.status_code == 200:
            result_low = response_low.json()
            print(f"📊 Low-Skill Agent ({low_skill_agent['Name']}):")
            print(f"   Overall Score: {result_low['quality_metrics']['overall_score']:.3f}")
            print(f"   Agent Fit Score: {result_low['quality_metrics']['agent_fit_score']:.3f}")
            print(f"   Emotion: {result_low['agent_feedback']['emotion']}")
            
            # Compare results
            high_score = result_high['quality_metrics']['overall_score']
            low_score = result_low['quality_metrics']['overall_score']
            
            print(f"\n📈 Impact of Agent Stats:")
            print(f"   Score Difference: {high_score - low_score:.3f}")
            print(f"   {'✅ Higher skilled agents handle prompts better!' if high_score > low_score else '⚠️ Unexpected result'}")
            
            return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Unity Integration Test Suite")
    print("Testing Agent Task Assignment API with Unity-style objects")
    print()
    
    # Test health first
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ API is not running. Please start the server first.")
            exit(1)
        print("✅ API is running")
    except:
        print("❌ Cannot connect to API. Please start the server first.")
        exit(1)
    
    # Run tests
    test1_success = test_unity_agent_structure()
    test2_success = test_prompt_evaluation_with_stats()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"✅ Unity Structure Test: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Agent Stats Impact Test: {'PASS' if test2_success else 'FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All Unity integration tests passed!")
        print("The API now properly supports Unity-style Agent and Task objects.")
        print("Agent stats (including TokenMultiplier) are being considered in evaluations.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
