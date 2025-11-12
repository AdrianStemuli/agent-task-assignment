#!/usr/bin/env python3
"""
Script to verify Swagger documentation shows Unity object format
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def check_swagger_schema():
    """Check if the OpenAPI schema shows Unity object examples"""
    
    print("🔍 Checking Swagger/OpenAPI Schema...")
    
    try:
        # Get the OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json")
        
        if response.status_code == 200:
            schema = response.json()
            
            # Check TaskAssignmentRequest schema
            task_assignment_schema = schema.get("components", {}).get("schemas", {}).get("TaskAssignmentRequest", {})
            
            if task_assignment_schema:
                properties = task_assignment_schema.get("properties", {})
                
                # Check Agent field example
                agent_field = properties.get("Agent", {})
                agent_example = agent_field.get("example", {})
                
                print("📋 TaskAssignmentRequest Schema Check:")
                print(f"   Agent field found: {'✅' if agent_field else '❌'}")
                
                if agent_example:
                    has_id = "ID" in agent_example
                    has_stats = "Stats" in agent_example
                    has_stat_value_obj = False
                    
                    if has_stats and isinstance(agent_example["Stats"], list) and agent_example["Stats"]:
                        has_stat_value_obj = "StatValueObj" in agent_example["Stats"][0]
                    
                    print(f"   Agent has ID field: {'✅' if has_id else '❌'}")
                    print(f"   Agent has Stats array: {'✅' if has_stats else '❌'}")
                    print(f"   Stats use StatValueObj: {'✅' if has_stat_value_obj else '❌'}")
                    
                    if has_id and has_stats and has_stat_value_obj:
                        print("   🎉 Unity format detected in schema!")
                        return True
                    else:
                        print("   ⚠️  Schema still shows old format")
                        return False
                else:
                    print("   ❌ No example found in Agent field")
                    return False
            else:
                print("   ❌ TaskAssignmentRequest schema not found")
                return False
        else:
            print(f"   ❌ Failed to get OpenAPI schema: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking schema: {e}")
        return False

def test_actual_request():
    """Test that the API actually works with Unity format"""
    
    print("\n🧪 Testing Actual Unity Format Request...")
    
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
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/assign", json=unity_payload)
        
        if response.status_code == 201:
            result = response.json()
            print("   ✅ Unity format request successful!")
            print(f"   Task ID: {result['task_assignment']['task_id']}")
            return True
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Swagger Documentation Verification")
    print("Checking if Unity object format appears in Swagger UI")
    print()
    
    # Check API health
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ API not running. Please start the server first.")
            print("   Run: python main.py")
            exit(1)
        print("✅ API is running")
    except:
        print("❌ Cannot connect to API. Please start the server first.")
        exit(1)
    
    # Run checks
    schema_updated = check_swagger_schema()
    request_works = test_actual_request()
    
    print("\n" + "=" * 50)
    print("📊 Verification Results:")
    print(f"✅ Schema Updated: {'PASS' if schema_updated else 'FAIL'}")
    print(f"✅ Unity Format Works: {'PASS' if request_works else 'FAIL'}")
    
    if schema_updated and request_works:
        print("\n🎉 SUCCESS!")
        print("Swagger UI should now show Unity object format in examples.")
        print("Visit http://localhost:8001/docs to see the updated documentation.")
    else:
        print("\n⚠️  Issues detected:")
        if not schema_updated:
            print("- Swagger schema may need server restart to update")
        if not request_works:
            print("- Unity format requests are not working properly")
        
        print("\nTry restarting the server: python main.py")
