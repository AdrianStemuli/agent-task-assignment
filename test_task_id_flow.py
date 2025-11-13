#!/usr/bin/env python3
"""
Test script for the updated task_id flow in task assignment and completion
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_task_assignment_and_completion():
    """Test the complete task_id flow from assignment to completion"""
    
    print("🧪 Testing Task ID Flow")
    print("=" * 40)
    
    # Step 1: Assign a task
    print("\n1️⃣ Assigning task...")
    
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
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
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
            
            # Extract task_assignment and task_id
            task_assignment = assignment_data.get("task_assignment")
            if task_assignment:
                task_id = task_assignment.get("task_id")
                assigned_task = task_assignment.get("task")
                
                print(f"📋 Task ID: {task_id}")
                print(f"📋 Task in assignment: {assigned_task.get('task_id') if assigned_task else 'N/A'}")
                
                # Step 2: Complete the task using the task_id from the Task object
                print(f"\n2️⃣ Completing task with ID: {task_id}")
                
                completion_payload = {
                    "Agent": assignment_payload["Agent"],  # Same agent
                    "Task": {
                        "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
                        "Title": "Write Marketing Email",
                        "Description": "Create an email campaign to increase customer retention",
                        "Category": "EMAIL_CAMPAIGN",
                        "task_id": task_id  # This is the key change - task_id in Task object
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

def test_completion_without_task_id():
    """Test that completion fails when task_id is missing from Task object"""
    
    print("\n🧪 Testing Completion Without Task ID")
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
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write Marketing Email",
            "Description": "Create an email campaign",
            "Category": "EMAIL_CAMPAIGN"
            # No task_id field - should fail
        },
        "Prompt": "Write an email campaign"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/complete", json=completion_payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctly rejected completion without task_id")
            return True
        else:
            print("❌ Should have rejected completion without task_id")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def test_completion_with_invalid_task_id():
    """Test that completion fails when task_id doesn't exist"""
    
    print("\n🧪 Testing Completion With Invalid Task ID")
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
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write Marketing Email",
            "Description": "Create an email campaign",
            "Category": "EMAIL_CAMPAIGN",
            "task_id": "task_nonexistent123"  # Invalid task_id
        },
        "Prompt": "Write an email campaign"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/complete", json=completion_payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly rejected completion with invalid task_id")
            return True
        else:
            print("❌ Should have rejected completion with invalid task_id")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Updated Task ID Flow")
    print("=" * 50)
    
    # Test all scenarios
    test1 = test_task_assignment_and_completion()
    test2 = test_completion_without_task_id()
    test3 = test_completion_with_invalid_task_id()
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Full Task Flow: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Missing Task ID: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Invalid Task ID: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! Task ID flow is working correctly.")
        print("\n📋 Summary of Changes:")
        print("- Task assignment now returns task_assignment with task_id")
        print("- Task object now includes task_id field for completion tracking")
        print("- Task completion uses task_id from Task object in request body")
        print("- Proper validation for missing/invalid task_id")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
