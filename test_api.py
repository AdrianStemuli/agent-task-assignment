#!/usr/bin/env python3
"""
Quick test script for the Agent Task Assignment API
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_assign_task():
    """Test the task assignment endpoint with simple string inputs"""
    url = f"{BASE_URL}/tasks/assign"
    
    payload = {
        "Agent": "test",
        "Task": "solve problem",
        "Prompt": "You have been given a task to solve a math problem"
    }
    
    print("Testing /tasks/assign endpoint...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_evaluate_prompt():
    """Test the prompt evaluation endpoint"""
    url = f"{BASE_URL}/prompts/evaluate"
    
    payload = {
        "Agent": "test",
        "Task": "solve problem", 
        "Prompt": "You have been given a task to solve a math problem"
    }
    
    print("\nTesting /prompts/evaluate endpoint...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Agent Task Assignment API")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {health_response.status_code}")
        print(f"Health Data: {json.dumps(health_response.json(), indent=2)}")
    except Exception as e:
        print(f"Health check failed: {e}")
        exit(1)
    
    print("\n" + "=" * 50)
    
    # Test endpoints
    assign_success = test_assign_task()
    evaluate_success = test_evaluate_prompt()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Task Assignment: {'PASS' if assign_success else 'FAIL'}")
    print(f"✅ Prompt Evaluation: {'PASS' if evaluate_success else 'FAIL'}")
    
    if assign_success and evaluate_success:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
