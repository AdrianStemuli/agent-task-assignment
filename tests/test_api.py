"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_tasks" in data


def test_assign_task():
    """Test task assignment endpoint"""
    request_data = {
        "Agent": {
            "Name": "Bob",
            "Department": "Research",
            "Stats": [
                {"Name": "Expertise", "Value": 5},
                {"Name": "Quality", "Value": 5},
                {"Name": "Reliability", "Value": 6},
                {"Name": "Speed", "Value": 3},
                {"Name": "Capacity", "Value": 2}
            ]
        },
        "Task": {
            "Title": "Write email",
            "Description": "Write an email to Alice"
        },
        "Prompt": {
            "Text": "Write an email to Alice",
            "Parameters": [
                {"Name": "Agency", "Value": 1},
                {"Name": "Clarity", "Value": 5}
            ]
        }
    }
    
    response = client.post("/tasks/assign", json=request_data)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "task_assignment" in data
    assert data["task_assignment"]["agent_name"] == "Bob"


def test_list_tasks():
    """Test listing tasks"""
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert "pending" in data


def test_get_nonexistent_task():
    """Test getting a task that doesn't exist"""
    response = client.get("/tasks/nonexistent_task_id")
    assert response.status_code == 404


def test_invalid_agent_stats():
    """Test task assignment with invalid agent stats"""
    request_data = {
        "Agent": {
            "Name": "Bob",
            "Department": "Research",
            "Stats": [
                {"Name": "Expertise", "Value": 15},  # Invalid: too high
            ]
        },
        "Task": {
            "Title": "Write email",
            "Description": "Write an email"
        },
        "Prompt": {
            "Text": "Write an email",
            "Parameters": []
        }
    }
    
    response = client.post("/tasks/assign", json=request_data)
    assert response.status_code == 422  # Validation error


def test_get_agent_tasks():
    """Test getting tasks for a specific agent"""
    # First assign a task
    request_data = {
        "Agent": {
            "Name": "Alice",
            "Department": "Marketing",
            "Stats": [
                {"Name": "Expertise", "Value": 7},
                {"Name": "Quality", "Value": 8},
                {"Name": "Reliability", "Value": 7},
                {"Name": "Speed", "Value": 6},
                {"Name": "Capacity", "Value": 5}
            ]
        },
        "Task": {
            "Title": "Social media campaign",
            "Description": "Create a social media campaign"
        },
        "Prompt": {
            "Text": "Create a social media campaign",
            "Parameters": []
        }
    }
    
    client.post("/tasks/assign", json=request_data)
    
    # Get tasks for Alice
    response = client.get("/agents/Alice/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "Alice"
    assert "tasks" in data
    assert len(data["tasks"]) > 0
