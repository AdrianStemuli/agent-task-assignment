#!/usr/bin/env python3
"""
Quick test to verify the fix works
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_unity_format():
    """Test Unity object format"""
    payload = {
        "Agent": {
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
        },
        "Task": {
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write Marketing Email",
            "Description": "Write an email campaign to increase customer retention"
        },
        "Prompt": "Please write a professional email campaign to increase customer retention."
    }
    
    print("🧪 Quick Unity Format Test")
    print("=" * 40)
    
    try:
        print("Testing task assignment...")
        response = requests.post(f"{BASE_URL}/tasks/assign", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SUCCESS! Unity format is working!")
            print(f"Task ID: {result['task_assignment']['task_id']}")
            print(f"Agent: {result['task_assignment']['agent_name']}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_unity_format()
    if success:
        print("\n🎉 Ready to run full test suite!")
    else:
        print("\n🔧 Server needs to be restarted with the fixes.")
        print("Please restart the server: python main.py")
