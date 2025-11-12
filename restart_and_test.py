#!/usr/bin/env python3
"""
Script to test after server restart
"""

import requests
import time

BASE_URL = "http://localhost:8001"

def wait_for_server():
    """Wait for server to be ready"""
    print("Waiting for server to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    
    print("❌ Server not ready after 30 seconds")
    return False

def test_task_completion():
    """Test task completion after server restart"""
    
    if not wait_for_server():
        return False
    
    print("\n🧪 Testing Task Completion After Restart")
    print("=" * 45)
    
    # Create task
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
    
    try:
        # Step 1: Create task
        print("Step 1: Creating task...")
        assign_response = requests.post(f"{BASE_URL}/tasks/assign", json={
            "Agent": unity_agent,
            "Task": unity_task,
            "Prompt": prompt
        })
        
        if assign_response.status_code != 201:
            print(f"❌ Task creation failed: {assign_response.json()}")
            return False
        
        task_id = assign_response.json()["task_assignment"]["task_id"]
        print(f"✅ Task created: {task_id}")
        
        # Step 2: Complete task
        print("Step 2: Completing task...")
        complete_response = requests.post(f"{BASE_URL}/tasks/complete", json={
            "task_id": task_id,
            "Agent": unity_agent,
            "Task": unity_task,
            "Prompt": prompt
        })
        
        if complete_response.status_code == 200:
            result = complete_response.json()
            print("✅ Task completion successful!")
            print(f"   Options: {len(result['outcome']['options'])}")
            print(f"   Quality Score: {result['outcome']['prompt_quality_score']:.3f}")
            return True
        else:
            print(f"❌ Task completion failed: {complete_response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Testing After Server Restart")
    print("Make sure you've restarted the server with: python main.py")
    print()
    
    success = test_task_completion()
    
    if success:
        print("\n🎉 Task completion is now working!")
        print("Ready to run full test suite!")
    else:
        print("\n🔧 Task completion still has issues.")
        print("The server may need to be restarted to pick up the fixes.")
