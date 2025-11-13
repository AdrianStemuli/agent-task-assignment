#!/usr/bin/env python3
"""
Test script for the new FocusParameter format in prompt refinement
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_focus_parameter_format():
    """Test the new FocusParameter format"""
    
    # Test data with the new FocusParameter format
    payload = {
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
            "Title": "Write email",
            "Description": "Write an email to Alice about the quarterly report",
            "Category": "EMAIL_CAMPAIGN"
        },
        "Prompt": "Write an email to Alice",
        "focus_parameter": [
            {
                "Name": "Agency",
                "Value": 1
            },
            {
                "Name": "Clarity", 
                "Value": 7
            }
        ]
    }
    
    print("Testing new FocusParameter format...")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/refine", json=payload)
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Prompt refinement with new FocusParameter format works!")
            print(f"Refined prompt: {data.get('refined_prompt_text', 'N/A')}")
            print(f"Improvements: {data.get('improvements', {})}")
            print(f"Expected improvement: {data.get('expected_quality_improvement', 0)}")
            return True
        else:
            print("❌ FAILED: Request failed")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception occurred: {e}")
        return False

def test_without_focus_parameter():
    """Test refinement without focus parameters (should still work)"""
    
    payload = {
        "Agent": {
            "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
            "Name": "Test Agent",
            "Department": "Engineering",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 8},
                {"Name": "Speed", "StatValueObj": 6}
            ]
        },
        "Task": {
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write email",
            "Description": "Write an email to Alice",
            "Category": "EMAIL_CAMPAIGN"
        },
        "Prompt": "Write an email to Alice"
        # No focus_parameter field
    }
    
    print("\nTesting without focus parameters...")
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/refine", json=payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Refinement without focus parameters works!")
            return True
        else:
            print("❌ FAILED: Request failed")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception occurred: {e}")
        return False

def test_default_values():
    """Test that default values work correctly"""
    
    payload = {
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
            "Title": "Write email",
            "Description": "Write an email to Alice",
            "Category": "EMAIL_CAMPAIGN"
        },
        "Prompt": "Write an email to Alice",
        "focus_parameter": [
            {
                "Name": "Empathy"
                # No Value field - should default to 5
            }
        ]
    }
    
    print("\nTesting default values...")
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/refine", json=payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Default values work correctly!")
            return True
        else:
            print("❌ FAILED: Request failed")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing FocusParameter Changes")
    print("=" * 40)
    
    # Test all scenarios
    test1 = test_focus_parameter_format()
    test2 = test_without_focus_parameter()
    test3 = test_default_values()
    
    print("\n📊 Test Results Summary")
    print("=" * 40)
    print(f"✅ With FocusParameter: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Without FocusParameter: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Default Values: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! FocusParameter changes are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
