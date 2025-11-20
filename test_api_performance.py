"""
Test API endpoint performance improvements
"""

import asyncio
import time
import json
import requests
from typing import Dict, Any


def test_task_completion_endpoint():
    """Test the actual API endpoint performance"""
    
    print("🚀 TESTING TASK COMPLETION API PERFORMANCE")
    print("="*60)
    
    # API endpoint
    base_url = "http://localhost:8001"
    
    # Test data
    test_request = {
        "Agent": {
            "ID": "test-agent-123",
            "Name": "Test Analyst",
            "Department": "Research",
            "Stats": [
                {"Name": "Expertise", "StatValueObj": 7},
                {"Name": "Quality", "StatValueObj": 6},
                {"Name": "Reliability", "StatValueObj": 8},
                {"Name": "Speed", "StatValueObj": 5},
                {"Name": "Capacity", "StatValueObj": 6}
            ],
            "autonomy_preference": 7,
            "preferred_tone": "professional"
        },
        "Task": {
            "ID": "test-task-456",
            "Title": "Quarterly Report Analysis",
            "Description": "Analyze Q3 financial data and prepare summary for stakeholders"
        },
        "Prompt": {
            "Text": "Please analyze the Q3 financial data and create a comprehensive summary report for our stakeholders. Focus on key metrics, trends, and actionable insights.",
            "Parameters": [
                {"Name": "Clarity", "Value": 8},
                {"Name": "Tone", "Value": 7},
                {"Name": "Agency", "Value": 6},
                {"Name": "Empathy", "Value": 7}
            ]
        }
    }
    
    # Test regular endpoint
    print("\n📊 Testing Regular Task Completion Endpoint...")
    regular_times = []
    
    for i in range(3):
        print(f"  Test {i+1}/3...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/tasks/complete",
                json=test_request,
                timeout=30
            )
            
            duration = time.time() - start_time
            regular_times.append(duration)
            
            if response.status_code == 200:
                result = response.json()
                print(f"    ✅ Success in {duration:.2f}s")
                print(f"    Quality Score: {result['outcome']['prompt_quality_score']:.3f}")
                print(f"    Options: {len(result['outcome']['options'])}")
            else:
                print(f"    ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            duration = 30  # Timeout
            regular_times.append(duration)
        
        time.sleep(1)  # Brief pause between tests
    
    # Test benchmark endpoint
    print("\n⚡ Testing Benchmark Endpoint (Comparison)...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/benchmark/task-completion",
            json=test_request,
            timeout=60
        )
        benchmark_duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"    ✅ Benchmark completed in {benchmark_duration:.2f}s")
            
            benchmark_results = result.get("benchmark_results", {})
            print(f"\n📈 BENCHMARK RESULTS:")
            print(f"    Original Duration: {benchmark_results.get('original_duration_seconds', 'N/A')}s")
            print(f"    Parallel Duration: {benchmark_results.get('parallel_duration_seconds', 'N/A')}s")
            print(f"    Performance Improvement: {benchmark_results.get('performance_improvement_percent', 'N/A')}%")
            print(f"    Speedup Factor: {benchmark_results.get('speedup_factor', 'N/A')}x")
            
            quality_comparison = result.get("quality_comparison", {})
            print(f"\n🎯 QUALITY COMPARISON:")
            print(f"    Original Quality: {quality_comparison.get('original_quality_score', 'N/A')}")
            print(f"    Parallel Quality: {quality_comparison.get('parallel_quality_score', 'N/A')}")
            print(f"    Quality Difference: {quality_comparison.get('quality_difference', 'N/A')}")
            
            recommendation = result.get("recommendation", "No recommendation")
            print(f"\n💡 RECOMMENDATION: {recommendation}")
            
        else:
            print(f"    ❌ Benchmark failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"    ❌ Benchmark error: {e}")
    
    # Analyze regular endpoint results
    if regular_times:
        avg_time = sum(regular_times) / len(regular_times)
        min_time = min(regular_times)
        max_time = max(regular_times)
        
        print(f"\n📊 REGULAR ENDPOINT ANALYSIS:")
        print(f"    Average Time: {avg_time:.2f}s")
        print(f"    Min Time: {min_time:.2f}s")
        print(f"    Max Time: {max_time:.2f}s")
        print(f"    Tests Completed: {len([t for t in regular_times if t < 30])}/3")
    
    print("\n" + "="*60)


def test_server_status():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on http://localhost:8001")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to run: python main.py")
        return False


def main():
    """Main test function"""
    print("🔧 TASK COMPLETION API PERFORMANCE TEST")
    print("="*60)
    
    # Check server status
    if not test_server_status():
        return
    
    # Run performance tests
    test_task_completion_endpoint()
    
    print("\n✅ Performance testing completed!")
    print("\n📋 SUMMARY OF OPTIMIZATIONS IMPLEMENTED:")
    print("   1. ✅ Parallel OpenAI calls in ParallelOutcomeGenerator")
    print("   2. ✅ Concurrent prompt evaluation and outcome generation")
    print("   3. ✅ Multiple focused API calls instead of one large call")
    print("   4. ✅ Optimized parameter handling for newer OpenAI models")
    print("   5. ✅ Benchmark endpoint for performance comparison")
    
    print("\n🎯 EXPECTED IMPROVEMENTS:")
    print("   • 30-60% faster response times")
    print("   • Better resource utilization")
    print("   • Same or improved output quality")
    print("   • More scalable architecture")


if __name__ == "__main__":
    main()
