#!/usr/bin/env python3
"""
Test the Unity object conversion fix
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_unity_objects():
    """Test Unity object format with the exact structure from the error"""
    
    unity_payload = {
        "Agent": {
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
        },
        "Task": {
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write email",
            "Description": "Write an email to Alice"
        },
        "Prompt": "Please write a professional email to Alice regarding the quarterly report."
    }
    
    print("🧪 Testing Unity Object Conversion Fix")
    print("=" * 50)
    print("Testing the exact Unity object structure that was failing...")
    print()
    
    try:
        print("📋 Testing Task Assignment...")
        response = requests.post(f"{BASE_URL}/tasks/assign", json=unity_payload)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SUCCESS! Task assignment worked!")
            print(f"   Task ID: {result['task_assignment']['task_id']}")
            print(f"   Agent Name: {result['task_assignment']['agent_name']}")
            print(f"   Message: {result['message']}")
            
            # Test prompt evaluation too
            print("\n🎯 Testing Prompt Evaluation...")
            eval_response = requests.post(f"{BASE_URL}/prompts/evaluate", json=unity_payload)
            
            if eval_response.status_code == 200:
                eval_result = eval_response.json()
                print("✅ SUCCESS! Prompt evaluation worked!")
                print(f"   Overall Score: {eval_result['quality_metrics']['overall_score']:.3f}")
                print(f"   Agent Emotion: {eval_result['agent_feedback']['emotion']}")
                return True
            else:
                print(f"❌ Prompt evaluation failed: {eval_response.status_code}")
                print(f"   Error: {eval_response.json()}")
                return False
        else:
            print(f"❌ Task assignment failed: {response.status_code}")
            error_detail = response.json()
            print(f"   Error: {error_detail}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Unity Object Conversion Fix Test")
    print("This test verifies that Unity objects are properly converted to Agent/Task models")
    print()
    
    # Check API health
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ API not running. Please start the server first.")
            exit(1)
        print("✅ API is running")
        print()
    except:
        print("❌ Cannot connect to API. Please start the server first.")
        exit(1)
    
    # Run test
    success = test_unity_objects()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 FIX SUCCESSFUL!")
        print("Unity objects are now properly converted to Agent and Task models.")
        print("The 'dict' object has no attribute 'Name' error should be resolved.")
    else:
        print("❌ Fix not working yet. Check the error messages above.")
