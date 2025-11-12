#!/usr/bin/env python3
"""
Quick test to verify Unity object format works correctly
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_unity_format():
    """Test the Unity object format"""
    
    # Unity-style objects exactly as specified
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
    
    unity_task = {
        "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
        "Title": "Write email",
        "Description": "Write an email to Alice"
    }
    
    prompt = "Please write a professional email to Alice regarding the quarterly report."
    
    print("🧪 Testing Unity Object Format")
    print("=" * 50)
    print(f"Agent ID: {unity_agent['ID']}")
    print(f"Agent Name: {unity_agent['Name']}")
    print(f"Task ID: {unity_task['ID']}")
    print(f"Task Title: {unity_task['Title']}")
    print()
    
    # Test task assignment
    print("📋 Testing Task Assignment...")
    assign_payload = {
        "Agent": unity_agent,
        "Task": unity_task,
        "Prompt": prompt
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/assign", json=assign_payload)
        if response.status_code == 201:
            result = response.json()
            print("✅ Task Assignment SUCCESS!")
            print(f"   Task ID: {result['task_assignment']['task_id']}")
            print(f"   Agent: {result['task_assignment']['agent_name']}")
            print(f"   Message: {result['message']}")
            return True
        else:
            print(f"❌ Task Assignment FAILED: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Task Assignment ERROR: {e}")
        return False

def test_prompt_evaluation():
    """Test prompt evaluation with Unity format"""
    
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
    
    unity_task = {
        "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
        "Title": "Write email",
        "Description": "Write an email to Alice"
    }
    
    prompt = "Please write a professional email to Alice regarding the quarterly report."
    
    print("🎯 Testing Prompt Evaluation...")
    eval_payload = {
        "Agent": unity_agent,
        "Task": unity_task,
        "Prompt": prompt
    }
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/evaluate", json=eval_payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Prompt Evaluation SUCCESS!")
            print(f"   Overall Score: {result['quality_metrics']['overall_score']:.3f}")
            print(f"   Agent Emotion: {result['agent_feedback']['emotion']}")
            print(f"   Agent Fit Score: {result['quality_metrics']['agent_fit_score']:.3f}")
            return True
        else:
            print(f"❌ Prompt Evaluation FAILED: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Prompt Evaluation ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎮 Unity Format Compatibility Test")
    print("Testing the exact object structure from Unity")
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
    assign_success = test_unity_format()
    eval_success = test_prompt_evaluation()
    
    print()
    print("=" * 50)
    print("📊 Test Results:")
    print(f"✅ Task Assignment: {'PASS' if assign_success else 'FAIL'}")
    print(f"✅ Prompt Evaluation: {'PASS' if eval_success else 'FAIL'}")
    
    if assign_success and eval_success:
        print()
        print("🎉 SUCCESS! Unity object format works perfectly!")
        print("The API now correctly handles your Unity agent and task objects.")
    else:
        print()
        print("❌ Some tests failed. Check the errors above.")
