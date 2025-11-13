#!/usr/bin/env python3
"""
Test script for the Unity Task.ID flow in task assignment and completion
"""

import requests
import json

BASE_URL = "http://localhost:8001"  # Updated to match the server port

def test_task_assignment_and_completion_with_unity_id():
    """Test the complete Task.ID flow from assignment to completion"""
    
    print("🧪 Testing Unity Task.ID Flow")
    print("=" * 40)
    
    # Unity Task ID that will be used throughout the flow
    unity_task_id = "e84f8439-8072-4b02-85b0-44d0dad335b7"
    
    # Step 1: Assign a task
    print(f"\n1️⃣ Assigning task with Unity ID: {unity_task_id}")
    
    assignment_payload = {
        "Agent": {
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Test Agent",
            "Department": "Engineering",
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
            "ID": unity_task_id,  # Unity's task ID
            "Title": "Write Marketing Email",
            "Description": "Create an email campaign to increase customer retention",
            "Category": "EMAIL_CAMPAIGN"
        },
        "Prompt": "Please write a professional email campaign to increase customer retention. Focus on value proposition and personalization."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/assign", json=assignment_payload)
        print(f"Assignment response status: {response.status_code}")
        
        if response.status_code == 201:
            assignment_data = response.json()
            print("✅ Task assignment successful!")
            
            # Extract task_assignment
            task_assignment = assignment_data.get("task_assignment")
            if task_assignment:
                assigned_task = task_assignment.get("task")
                assigned_task_id = assigned_task.get("ID") if assigned_task else None
                
                print(f"📋 Assigned Task ID: {assigned_task_id}")
                print(f"📋 Matches Unity ID: {assigned_task_id == unity_task_id}")
                
                # Step 2: Complete the task using the same Unity Task ID
                print(f"\n2️⃣ Completing task with Unity ID: {unity_task_id}")
                
                completion_payload = {
                    "Agent": assignment_payload["Agent"],  # Same agent
                    "Task": {
                        "ID": unity_task_id,  # Same Unity task ID
                        "Title": "Write Marketing Email",
                        "Description": "Create an email campaign to increase customer retention",
                        "Category": "EMAIL_CAMPAIGN"
                    },
                    "Prompt": "Please write a professional email campaign to increase customer retention. Focus on value proposition, personalization, and clear call-to-action."
                }
                
                completion_response = requests.post(f"{BASE_URL}/tasks/complete", json=completion_payload)
                print(f"Completion response status: {completion_response.status_code}")
                
                if completion_response.status_code == 200:
                    completion_data = completion_response.json()
                    print("✅ Task completion successful!")
                    print(f"📊 Outcome: {completion_data.get('outcome', {}).get('summary', 'N/A')}")
                    return True
                else:
                    print("❌ Task completion failed")
                    try:
                        error_data = completion_response.json()
                        print(f"Error details: {error_data}")
                    except:
                        print(f"Error text: {completion_response.text}")
                    return False
            else:
                print("❌ No task_assignment in response")
                return False
        else:
            print("❌ Task assignment failed")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def test_completion_with_different_task_id():
    """Test that completion fails when using a different Task ID"""
    
    print("\n🧪 Testing Completion With Different Task ID")
    print("=" * 40)
    
    completion_payload = {
        "Agent": {
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Test Agent",
            "Department": "Engineering",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 8}
            ]
        },
        "Task": {
            "ID": "different-task-id-12345",  # Different task ID
            "Title": "Write Marketing Email",
            "Description": "Create an email campaign",
            "Category": "EMAIL_CAMPAIGN"
        },
        "Prompt": "Write an email campaign"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/complete", json=completion_payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly rejected completion with non-existent Task ID")
            return True
        else:
            print("❌ Should have rejected completion with non-existent Task ID")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def test_multiple_tasks_with_different_ids():
    """Test assigning multiple tasks with different Unity IDs"""
    
    print("\n🧪 Testing Multiple Tasks With Different Unity IDs")
    print("=" * 40)
    
    task_ids = [
        "unity-task-001",
        "unity-task-002", 
        "unity-task-003"
    ]
    
    success_count = 0
    
    for i, task_id in enumerate(task_ids):
        print(f"\nAssigning task {i+1} with ID: {task_id}")
        
        assignment_payload = {
            "Agent": {
                "ID": f"agent-{i+1}",
                "Name": f"Agent {i+1}",
                "Department": "Engineering",
                "Stats": [{"Name": "Expertise", "StatValueObj": 7}]
            },
            "Task": {
                "ID": task_id,
                "Title": f"Task {i+1}",
                "Description": f"Description for task {i+1}",
                "Category": "CUSTOM"
            },
            "Prompt": f"Complete task {i+1}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tasks/assign", json=assignment_payload)
            if response.status_code == 201:
                print(f"✅ Task {i+1} assigned successfully")
                success_count += 1
            else:
                print(f"❌ Task {i+1} assignment failed")
        except Exception as e:
            print(f"❌ Exception for task {i+1}: {e}")
    
    print(f"\n📊 Successfully assigned {success_count}/{len(task_ids)} tasks")
    return success_count == len(task_ids)

if __name__ == "__main__":
    print("🚀 Testing Unity Task.ID Flow")
    print("=" * 50)
    
    # Test all scenarios
    test1 = test_task_assignment_and_completion_with_unity_id()
    test2 = test_completion_with_different_task_id()
    test3 = test_multiple_tasks_with_different_ids()
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Unity ID Flow: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Different Task ID: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Multiple Tasks: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! Unity Task.ID flow is working correctly.")
        print("\n📋 Summary of Changes:")
        print("- Task assignment now uses Task.ID directly (no generated task_id)")
        print("- Task completion uses Task.ID from request body")
        print("- TaskAssignment.task_id property returns Task.ID")
        print("- Simplified flow: Unity ID → Assignment → Completion")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
