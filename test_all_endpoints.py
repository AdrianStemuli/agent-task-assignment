#!/usr/bin/env python3
"""
Comprehensive test suite for all API endpoints
Tests both Unity object format and string format for backward compatibility
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

class APITester:
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        if success:
            print(f"✅ {test_name}")
            self.results["passed"] += 1
        else:
            print(f"❌ {test_name}")
            if details:
                print(f"   Error: {details}")
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
    
    def get_unity_agent(self) -> Dict[str, Any]:
        """Get a Unity-format agent object"""
        return {
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
    
    def get_unity_task(self) -> Dict[str, Any]:
        """Get a Unity-format task object"""
        return {
            "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
            "Title": "Write Marketing Email",
            "Description": "Write an email campaign to increase customer retention"
        }
    
    def get_low_skill_agent(self) -> Dict[str, Any]:
        """Get a low-skill agent for comparison tests"""
        return {
            "ID": "b88f99df-3ed6-5bcc-9f8g-f93d4dd446d4",
            "Name": "Junior Intern",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 2},
                {"Name": "Speed", "StatValueObj": 3},
                {"Name": "Reliability", "StatValueObj": 2},
                {"Name": "Quality", "StatValueObj": 1},
                {"Name": "Capacity", "StatValueObj": 2},
                {"Name": "TokenMultiplier", "StatValueObj": 0.5}
            ]
        }

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True)
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid health response format")
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, str(e))
        return False

    def test_task_assignment_unity_format(self):
        """Test task assignment with Unity object format"""
        payload = {
            "Agent": self.get_unity_agent(),
            "Task": self.get_unity_task(),
            "Prompt": "Please write a professional email campaign to increase customer retention. Focus on highlighting our value proposition and include a clear call-to-action."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tasks/assign", json=payload)
            if response.status_code == 201:
                data = response.json()
                required_fields = ["task_assignment", "message", "initial_feedback"]
                if all(field in data for field in required_fields):
                    task_id = data["task_assignment"]["task_id"]
                    self.log_result("Task Assignment (Unity Format)", True)
                    return task_id
                else:
                    self.log_result("Task Assignment (Unity Format)", False, "Missing required response fields")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Task Assignment (Unity Format)", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Task Assignment (Unity Format)", False, str(e))
        return None

    def test_task_assignment_string_format(self):
        """Test task assignment with string format (backward compatibility)"""
        payload = {
            "Agent": "Marketing Specialist",
            "Task": "Create social media campaign",
            "Prompt": "Create an engaging social media campaign for our new product launch."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tasks/assign", json=payload)
            if response.status_code == 201:
                data = response.json()
                if "task_assignment" in data and "task_id" in data["task_assignment"]:
                    self.log_result("Task Assignment (String Format)", True)
                    return data["task_assignment"]["task_id"]
                else:
                    self.log_result("Task Assignment (String Format)", False, "Invalid response format")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Task Assignment (String Format)", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Task Assignment (String Format)", False, str(e))
        return None

    def test_prompt_evaluation_unity_format(self):
        """Test prompt evaluation with Unity objects"""
        payload = {
            "Agent": self.get_unity_agent(),
            "Task": self.get_unity_task(),
            "Prompt": "Write an email campaign to increase customer retention."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/prompts/evaluate", json=payload)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["quality_metrics", "agent_feedback", "suggestions", "is_ready"]
                if all(field in data for field in required_fields):
                    score = data["quality_metrics"]["overall_score"]
                    emotion = data["agent_feedback"]["emotion"]
                    self.log_result(f"Prompt Evaluation (Unity) - Score: {score:.3f}, Emotion: {emotion}", True)
                    return data
                else:
                    self.log_result("Prompt Evaluation (Unity Format)", False, "Missing required response fields")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Prompt Evaluation (Unity Format)", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Prompt Evaluation (Unity Format)", False, str(e))
        return None

    def test_prompt_evaluation_string_format(self):
        """Test prompt evaluation with string format"""
        payload = {
            "Agent": "Content Writer",
            "Task": "Write blog post",
            "Prompt": "Write a blog post about AI trends."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/prompts/evaluate", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "quality_metrics" in data and "overall_score" in data["quality_metrics"]:
                    score = data["quality_metrics"]["overall_score"]
                    self.log_result(f"Prompt Evaluation (String) - Score: {score:.3f}", True)
                    return data
                else:
                    self.log_result("Prompt Evaluation (String Format)", False, "Invalid response format")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Prompt Evaluation (String Format)", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Prompt Evaluation (String Format)", False, str(e))
        return None

    def test_agent_stats_impact(self):
        """Test that agent stats significantly impact evaluation scores"""
        high_skill_agent = self.get_unity_agent()
        low_skill_agent = self.get_low_skill_agent()
        task = self.get_unity_task()
        prompt = "Please write a professional email campaign to increase customer retention."
        
        # Test high-skill agent
        high_payload = {"Agent": high_skill_agent, "Task": task, "Prompt": prompt}
        low_payload = {"Agent": low_skill_agent, "Task": task, "Prompt": prompt}
        
        try:
            high_response = requests.post(f"{BASE_URL}/prompts/evaluate", json=high_payload)
            low_response = requests.post(f"{BASE_URL}/prompts/evaluate", json=low_payload)
            
            if high_response.status_code == 200 and low_response.status_code == 200:
                high_data = high_response.json()
                low_data = low_response.json()
                
                high_score = high_data["quality_metrics"]["overall_score"]
                low_score = low_data["quality_metrics"]["overall_score"]
                
                score_diff = high_score - low_score
                
                if score_diff > 0.1:  # Expect at least 0.1 difference
                    self.log_result(f"Agent Stats Impact - High: {high_score:.3f}, Low: {low_score:.3f}, Diff: {score_diff:.3f}", True)
                    return True
                else:
                    self.log_result("Agent Stats Impact", False, f"Insufficient score difference: {score_diff:.3f}")
            else:
                self.log_result("Agent Stats Impact", False, "Failed to get evaluation responses")
        except Exception as e:
            self.log_result("Agent Stats Impact", False, str(e))
        return False

    def test_prompt_refinement(self):
        """Test prompt refinement endpoint"""
        payload = {
            "Agent": self.get_unity_agent(),
            "Task": self.get_unity_task(),
            "Prompt": "Write email",
            "focus_parameter": "Clarity"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/prompts/refine", json=payload)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["refined_prompt_text", "improvements", "expected_quality_improvement"]
                if all(field in data for field in required_fields):
                    improvement = data["expected_quality_improvement"]
                    self.log_result(f"Prompt Refinement - Expected improvement: {improvement:.3f}", True)
                    return data
                else:
                    self.log_result("Prompt Refinement", False, "Missing required response fields")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Prompt Refinement", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Prompt Refinement", False, str(e))
        return None

    def test_prompt_generation(self):
        """Test prompt generation endpoint"""
        payload = {
            "Task": self.get_unity_task(),
            "Agent": self.get_unity_agent(),
            "style_preference": "professional"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/prompts/generate", json=payload)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["generated_prompts", "prompt_count", "task_category"]
                if all(field in data for field in required_fields):
                    count = data["prompt_count"]
                    category = data["task_category"]
                    customized = data.get("agent_customized", False)
                    self.log_result(f"Prompt Generation - {count} prompts, Category: {category}, Customized: {customized}", True)
                    return data
                else:
                    self.log_result("Prompt Generation", False, "Missing required response fields")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Prompt Generation", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Prompt Generation", False, str(e))
        return None

    def test_task_completion(self, task_id: str = None):
        """Test task completion endpoint"""
        if not task_id:
            # Create a task first
            task_id = self.test_task_assignment_unity_format()
            if not task_id:
                self.log_result("Task Completion", False, "Could not create task for completion test")
                return None
        
        payload = {
            "task_id": task_id,
            "Agent": self.get_unity_agent(),
            "Task": self.get_unity_task(),
            "Prompt": "Please write a professional email campaign to increase customer retention."
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tasks/complete", json=payload)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["outcome", "message"]
                if all(field in data for field in required_fields):
                    outcome = data["outcome"]
                    if "options" in outcome and len(outcome["options"]) > 0:
                        num_options = len(outcome["options"])
                        quality_score = outcome["prompt_quality_score"]
                        self.log_result(f"Task Completion - {num_options} options, Quality: {quality_score:.3f}", True)
                        return data
                    else:
                        self.log_result("Task Completion", False, "No outcome options generated")
                else:
                    self.log_result("Task Completion", False, "Missing required response fields")
            else:
                error_detail = response.json() if response.content else "No error details"
                self.log_result("Task Completion", False, f"Status {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_result("Task Completion", False, str(e))
        return None

    def test_error_handling(self):
        """Test error handling with invalid requests"""
        # Test with missing required fields
        invalid_payload = {"Agent": "Test"}  # Missing Task and Prompt
        
        try:
            response = requests.post(f"{BASE_URL}/tasks/assign", json=invalid_payload)
            if response.status_code == 422:  # Validation error
                self.log_result("Error Handling (Missing Fields)", True)
            else:
                self.log_result("Error Handling (Missing Fields)", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling (Missing Fields)", False, str(e))
        
        # Test with invalid JSON
        try:
            response = requests.post(f"{BASE_URL}/tasks/assign", data="invalid json")
            if response.status_code in [400, 422]:  # Bad request or validation error
                self.log_result("Error Handling (Invalid JSON)", True)
            else:
                self.log_result("Error Handling (Invalid JSON)", False, f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling (Invalid JSON)", False, str(e))

    def test_cors_headers(self):
        """Test CORS headers are present"""
        try:
            # Test CORS headers on a regular GET request
            response = requests.get(f"{BASE_URL}/health")
            headers = response.headers
            
            # Check for CORS headers
            has_origin = "access-control-allow-origin" in [h.lower() for h in headers.keys()]
            
            if has_origin:
                self.log_result("CORS Headers", True)
            else:
                # Try OPTIONS request as fallback
                try:
                    options_response = requests.options(f"{BASE_URL}/health")
                    options_headers = options_response.headers
                    has_cors_options = any("access-control" in h.lower() for h in options_headers.keys())
                    
                    if has_cors_options:
                        self.log_result("CORS Headers (OPTIONS)", True)
                    else:
                        self.log_result("CORS Headers", False, "No CORS headers found in GET or OPTIONS")
                except:
                    self.log_result("CORS Headers", False, "No CORS headers found")
        except Exception as e:
            self.log_result("CORS Headers", False, str(e))

    def run_all_tests(self):
        """Run all test cases"""
        print("🧪 COMPREHENSIVE API TEST SUITE")
        print("=" * 60)
        print("Testing all endpoints with Unity object format and backward compatibility")
        print()
        
        # Check if API is running
        if not self.test_health_endpoint():
            print("❌ API is not running. Please start the server first.")
            return False
        
        print("\n📋 TASK ASSIGNMENT TESTS")
        print("-" * 30)
        task_id = self.test_task_assignment_unity_format()
        self.test_task_assignment_string_format()
        
        print("\n🎯 PROMPT EVALUATION TESTS")
        print("-" * 30)
        self.test_prompt_evaluation_unity_format()
        self.test_prompt_evaluation_string_format()
        self.test_agent_stats_impact()
        
        print("\n🔧 PROMPT REFINEMENT TESTS")
        print("-" * 30)
        self.test_prompt_refinement()
        
        print("\n🎯 PROMPT GENERATION TESTS")
        print("-" * 30)
        self.test_prompt_generation()
        
        print("\n✅ TASK COMPLETION TESTS")
        print("-" * 30)
        self.test_task_completion(task_id)
        
        print("\n⚠️  ERROR HANDLING TESTS")
        print("-" * 30)
        self.test_error_handling()
        
        print("\n🌐 CORS TESTS")
        print("-" * 30)
        self.test_cors_headers()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results["errors"]:
            print(f"\n❌ Failed Tests:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        if self.results["failed"] == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Unity object format is working correctly")
            print("✅ Agent stats are having significant impact")
            print("✅ All endpoints are functioning properly")
            print("✅ Error handling is working")
            return True
        else:
            print(f"\n⚠️  {self.results['failed']} tests failed. Check the errors above.")
            return False

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 API is ready for Unity integration!")
    else:
        print("\n🔧 Some issues need to be resolved before Unity integration.")
