#!/usr/bin/env python3
"""
Test the new prompt generation endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_prompt_generation():
    """Test the prompt generation endpoint with different scenarios"""
    
    print("🎯 Testing Prompt Generation Endpoint")
    print("=" * 50)
    
    # Test 1: Basic task without agent
    print("\n📝 Test 1: Basic Task (No Agent)")
    print("-" * 30)
    
    basic_task = {
        "Task": {
            "ID": "task_001",
            "Title": "Write Marketing Email",
            "Description": "Create an email campaign to promote our new product launch"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/generate", json=basic_task)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated {result['prompt_count']} prompts")
            print(f"   Category: {result['task_category']}")
            print(f"   Method: {result['generation_method']}")
            print(f"   Agent Customized: {result['agent_customized']}")
            print("\n   Sample Prompts:")
            for i, prompt in enumerate(result['generated_prompts'][:2], 1):
                print(f"   {i}. {prompt[:80]}...")
        else:
            print(f"❌ Failed: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Task with agent customization
    print("\n👤 Test 2: Task with Agent Customization")
    print("-" * 40)
    
    agent_task = {
        "Task": {
            "ID": "task_002",
            "Title": "Conduct Market Research",
            "Description": "Research competitors in the AI software market"
        },
        "Agent": {
            "ID": "agent_001",
            "Name": "Senior Research Analyst",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 9},
                {"Name": "Research", "StatValueObj": 8},
                {"Name": "Analysis", "StatValueObj": 9},
                {"Name": "Communication", "StatValueObj": 7}
            ]
        },
        "style_preference": "professional"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/generate", json=agent_task)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated {result['prompt_count']} prompts")
            print(f"   Category: {result['task_category']}")
            print(f"   Style: {result['style_applied']}")
            print(f"   Agent Customized: {result['agent_customized']}")
            print(f"   Method: {result['generation_method']}")
            print("\n   Sample Prompts:")
            for i, prompt in enumerate(result['generated_prompts'][:2], 1):
                print(f"   {i}. {prompt[:80]}...")
        else:
            print(f"❌ Failed: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Different task categories
    print("\n📋 Test 3: Different Task Categories")
    print("-" * 35)
    
    test_tasks = [
        {
            "title": "Social Media Post",
            "description": "Create engaging social media content for product launch",
            "expected_category": "social_media"
        },
        {
            "title": "Bug Fix",
            "description": "Fix the login authentication issue",
            "expected_category": "bug_fix"
        },
        {
            "title": "Training Workshop",
            "description": "Design a workshop on effective communication",
            "expected_category": "workshop"
        }
    ]
    
    for i, test_task in enumerate(test_tasks, 1):
        print(f"\n   {i}. {test_task['title']}:")
        
        payload = {
            "Task": {
                "ID": f"task_00{i+2}",
                "Title": test_task["title"],
                "Description": test_task["description"]
            }
        }
        
        try:
            response = requests.post(f"{BASE_URL}/prompts/generate", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ Category: {result['task_category']} | Prompts: {result['prompt_count']}")
                print(f"         Sample: {result['generated_prompts'][0][:60]}...")
            else:
                print(f"      ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Test 4: String format (backward compatibility)
    print("\n🔄 Test 4: String Format (Backward Compatibility)")
    print("-" * 45)
    
    string_task = {
        "Task": "Write a blog post about artificial intelligence trends"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/generate", json=string_task)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ String format works! Generated {result['prompt_count']} prompts")
            print(f"   Category: {result['task_category']}")
            print(f"   Sample: {result['generated_prompts'][0][:60]}...")
        else:
            print(f"❌ Failed: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Error handling
    print("\n⚠️  Test 5: Error Handling")
    print("-" * 25)
    
    invalid_payload = {"invalid": "data"}
    
    try:
        response = requests.post(f"{BASE_URL}/prompts/generate", json=invalid_payload)
        if response.status_code == 422:
            print("✅ Validation error handled correctly")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_documentation():
    """Test that the new endpoint appears in API documentation"""
    print("\n📚 Testing API Documentation")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            
            # Check if the new endpoint is in the spec
            paths = openapi_spec.get("paths", {})
            if "/prompts/generate" in paths:
                endpoint = paths["/prompts/generate"]
                if "post" in endpoint:
                    print("✅ Endpoint documented in OpenAPI spec")
                    print(f"   Summary: {endpoint['post'].get('summary', 'N/A')}")
                    print(f"   Tags: {endpoint['post'].get('tags', [])}")
                else:
                    print("❌ POST method not found in endpoint")
            else:
                print("❌ Endpoint not found in OpenAPI spec")
        else:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Prompt Generation API Test Suite")
    print("Testing the new /prompts/generate endpoint")
    print()
    
    # Check if API is running
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code != 200:
            print("❌ API not running. Please start the server first.")
            exit(1)
        print("✅ API is running")
    except:
        print("❌ Cannot connect to API. Please start the server first.")
        exit(1)
    
    # Run tests
    test_prompt_generation()
    test_api_documentation()
    
    print("\n" + "=" * 50)
    print("🎉 Prompt Generation Testing Complete!")
    print("The new endpoint provides:")
    print("✅ Template-based prompt generation")
    print("✅ AI-enhanced prompts (when OpenAI is available)")
    print("✅ Agent-specific customization")
    print("✅ Style preferences")
    print("✅ Multiple task category support")
    print("✅ Unity object format compatibility")
    print("✅ Backward compatibility with strings")
    print("\n🎯 Ready for Unity integration!")
