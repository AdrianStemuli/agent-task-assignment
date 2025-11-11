"""
Tests for Pydantic models
"""

import pytest
from models import (
    Agent, AgentStat, Department,
    Task, TaskCategory,
    Prompt, PromptParameter, PromptParameterType,
    OutcomeOption, OutcomeType, StatModifier
)


def test_agent_creation():
    """Test creating an agent"""
    agent = Agent(
        Name="Alice",
        Department=Department.MARKETING,
        Stats=[
            AgentStat(Name="Expertise", Value=7),
            AgentStat(Name="Quality", Value=8),
            AgentStat(Name="Reliability", Value=7),
            AgentStat(Name="Speed", Value=6),
            AgentStat(Name="Capacity", Value=5)
        ]
    )
    
    assert agent.Name == "Alice"
    assert agent.Department == Department.MARKETING
    assert len(agent.Stats) == 5
    assert agent.get_stat_value("Expertise") == 7
    assert agent.get_overall_skill_level() == 6.6


def test_agent_stat_validation():
    """Test agent stat value validation"""
    with pytest.raises(ValueError):
        AgentStat(Name="Expertise", Value=11)  # Too high
    
    with pytest.raises(ValueError):
        AgentStat(Name="Expertise", Value=0)  # Too low


def test_task_creation():
    """Test creating a task"""
    task = Task(
        Title="Write email campaign",
        Description="Create an email campaign for customer retention",
        Category=TaskCategory.EMAIL_CAMPAIGN
    )
    
    assert task.Title == "Write email campaign"
    assert task.Category == TaskCategory.EMAIL_CAMPAIGN


def test_prompt_creation():
    """Test creating a prompt"""
    prompt = Prompt(
        Text="Hey Bob! Write an email campaign.",
        Parameters=[
            PromptParameter(Name=PromptParameterType.CLARITY, Value=7),
            PromptParameter(Name=PromptParameterType.CONTEXT, Value=6)
        ]
    )
    
    assert prompt.Text == "Hey Bob! Write an email campaign."
    assert len(prompt.Parameters) == 2
    assert prompt.get_parameter_value("Clarity") == 7
    assert prompt.get_parameter_value("Context") == 6
    assert prompt.get_parameter_value("Empathy") == 5  # Default


def test_prompt_parameter_validation():
    """Test prompt parameter validation"""
    with pytest.raises(ValueError):
        PromptParameter(Name=PromptParameterType.CLARITY, Value=11)


def test_outcome_option_creation():
    """Test creating an outcome option"""
    option = OutcomeOption(
        option_id="outcome_1",
        title="Excellent Campaign",
        description="Bob created an amazing email campaign",
        outcome_type=OutcomeType.BUFF,
        stat_modifiers=[
            StatModifier(stat_name="Revenue", change=15, percentage=True)
        ],
        narrative_text="The campaign was a huge success!"
    )
    
    assert option.title == "Excellent Campaign"
    assert option.outcome_type == OutcomeType.BUFF
    assert len(option.stat_modifiers) == 1
    assert option.stat_modifiers[0].change == 15


def test_stat_modifier():
    """Test stat modifier"""
    modifier = StatModifier(
        stat_name="Morale",
        change=-5,
        percentage=True
    )
    
    assert modifier.stat_name == "Morale"
    assert modifier.change == -5
    assert modifier.percentage is True
