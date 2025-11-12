#!/usr/bin/env python3
"""
Test just the task completion endpoint to debug the issue
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_task_completion_debug():
    """Debug the task completion issue"""
    
    # First create a task
    print("🔧 Debugging Task Completion")
    print("=" * 40)
    
    # Step 1: Create a task
    print("Step 1: Creating a task...")
    unity_agent = {
        "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
        "Name": "Senior Analyst",
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
        "Title": "Write Marketing Email",
        "Description": "Write an email campaign to increase customer retention"
    }
    
    prompt = "Please write a professional email campaign to increase customer retention."
    
    assign_payload = {
        "Agent": unity_agent,
        "Task": unity_task,
        "Prompt": prompt
    }
    
    try:
        assign_response = requests.post(f"{BASE_URL}/tasks/assign", json=assign_payload)
        if assign_response.status_code == 201:
            assign_result = assign_response.json()
            task_id = assign_result["task_assignment"]["task_id"]
            print(f"✅ Task created: {task_id}")
            
            # Step 2: Complete the task
            print("Step 2: Completing the task...")
            complete_payload = {
                "task_id": task_id,
                "Agent": unity_agent,
                "Task": unity_task,
                "Prompt": prompt
            }
            
            print("Payload being sent:")
            print(json.dumps(complete_payload, indent=2))
            
            complete_response = requests.post(f"{BASE_URL}/tasks/complete", json=complete_payload)
            print(f"Response status: {complete_response.status_code}")
            
            if complete_response.status_code == 200:
                complete_result = complete_response.json()
                print("✅ Task completion successful!")
                print(f"Outcome options: {len(complete_result['outcome']['options'])}")
                return True
            else:
                print("❌ Task completion failed!")
                error_detail = complete_response.json() if complete_response.content else "No error details"
                print(f"Error: {error_detail}")
                return False
        else:
            print("❌ Task creation failed!")
            print(f"Error: {assign_response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_task_completion_debug()
    if success:
        print("\n🎉 Task completion is working!")
    else:
        print("\n🔧 Task completion needs more debugging.")
