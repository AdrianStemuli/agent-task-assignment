# Agent Task Assignment System

A FastAPI-based system for managing agent task assignments with AI-powered prompt engineering features. This system teaches students the importance of effective prompting through an interactive, game-based approach.

## 🎯 Overview

This system enables:
- **Task Assignment**: Delegate tasks to agents with customizable prompts
- **Real-time Prompt Evaluation**: Get instant feedback on prompt quality
- **AI-Powered Refinement**: Receive suggestions to improve your prompts
- **Dynamic Outcomes**: Generate results based on prompt quality (better prompts = better outcomes)
- **Educational Feedback**: Learn prompt engineering through agent reactions and outcomes

## 🏗️ Architecture

```
agent-task-assignment/
├── config.py                 # Configuration and settings
├── main.py                   # FastAPI application
├── models/                   # Pydantic models
│   ├── agent.py             # Agent and department models
│   ├── task.py              # Task and assignment models
│   ├── prompt.py            # Prompt and parameter models
│   ├── outcome.py           # Outcome and result models
│   ├── requests.py          # API request models
│   └── responses.py         # API response models
├── services/                 # Business logic services
│   ├── openai_service.py    # OpenAI API integration
│   ├── prompt_evaluator.py  # Prompt quality evaluation
│   └── outcome_generator.py # Outcome generation
└── core/                     # Core business logic
    └── task_manager.py       # Task management logic
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ OR Docker
- OpenAI API key

### Option 1: Docker (Recommended)

1. **Quick Docker setup:**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   
   # Run with Docker
   ./docker-run.sh
   ```

2. **Manual Docker setup:**
   ```bash
   # Build and run
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

3. **Production deployment:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Option 2: Local Python Installation

1. **Quick setup with the provided script:**
   ```bash
   ./run.sh
   ```

2. **Manual setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   
   # Start the server
   python main.py
   ```

### Access the API
- API: http://localhost:8001
- Interactive Documentation: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

📚 **For detailed Docker instructions, see [DOCKER.md](DOCKER.md)**

## 📋 API Usage Examples

### 1. Assign a Task

```bash
POST /tasks/assign
```

Create a task assignment with an initial prompt:

```json
{
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
    "Title": "Write email campaign",
    "Description": "Write an email campaign that aims to increase retention"
  },
  "Prompt": {
    "Text": "Write an email to customers",
    "Parameters": [
      {"Name": "Clarity", "Value": 3},
      {"Name": "Context", "Value": 2}
    ]
  }
}
```

### 2. Evaluate Prompt Quality

```bash
POST /prompts/evaluate
```

Get real-time feedback on your prompt:

```json
{
  "Agent": {...},
  "Task": {...},
  "Prompt": {...}
}
```

**Response includes**:
- Overall quality score (0-1)
- Individual parameter scores (Clarity, Context, Tone, Agency, Empathy)
- Agent fit score
- Agent emotional reaction and feedback
- Suggestions for improvement
- Ready status (whether prompt is good enough)

### 3. Refine the Prompt

```bash
POST /prompts/refine
```

Get AI-powered suggestions to improve your prompt:

```json
{
  "Agent": {...},
  "Task": {...},
  "Prompt": {...},
  "focus_parameter": "Clarity"  // Optional: focus on specific parameter
}
```

**Response includes**:
- Refined prompt text
- Explanation of improvements
- Expected quality improvement

### 4. Complete the Task

```bash
POST /tasks/complete
```

Generate outcomes based on final prompt quality:

```json
{
  "task_id": "task_abc123",
  "Agent": {...},
  "Task": {...},
  "Prompt": {...}  // Final refined prompt
}
```

**Response includes**:
- 2-4 outcome options to choose from
- Stat modifiers (buffs/debuffs)
- Narrative text explaining results
- Agent feedback on the experience

## 🎓 Prompt Parameters

The system evaluates prompts based on 5 key parameters:

| Parameter | Range | Description |
|-----------|-------|-------------|
| **Clarity** | Vague (1) → Precise (10) | How specific and clear the instructions are |
| **Context** | Minimal (1) → Rich (10) | Amount of background information provided |
| **Tone** | Directive (1) → Empowering (10) | Communication style and motivation |
| **Agency** | Strict (1) → Freedom (10) | Balance between direction and autonomy |
| **Empathy** | None (1) → High (10) | Understanding of agent's perspective |

## 📊 Outcome Generation

Outcomes are dynamically generated based on prompt quality:

- **High Quality (0.8+)**: 3 positive outcomes with significant buffs
- **Good Quality (0.7-0.8)**: 2-3 outcomes, mostly positive
- **Medium Quality (0.5-0.7)**: Mixed outcomes (buffs and debuffs)
- **Low Quality (0.3-0.5)**: Mostly negative outcomes
- **Poor Quality (<0.3)**: All negative outcomes with debuffs

## 🔧 Configuration

Edit `config.py` or set environment variables:

```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
DEBUG=false
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 📝 Example Usage

### Complete Example Flow

```python
import requests

BASE_URL = "http://localhost:8001"

# 1. Assign task
response = requests.post(f"{BASE_URL}/tasks/assign", json={
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
        "Title": "Create social media campaign",
        "Description": "Design a social media campaign for product launch"
    },
    "Prompt": {
        "Text": "Create a social media campaign",
        "Parameters": []
    }
})
task_id = response.json()["task_assignment"]["task_id"]

# 2. Evaluate prompt
eval_response = requests.post(f"{BASE_URL}/prompts/evaluate", json={
    "Agent": {...},
    "Task": {...},
    "Prompt": {...}
})
quality_score = eval_response.json()["quality_metrics"]["overall_score"]

# 3. Refine if needed
if quality_score < 0.7:
    refine_response = requests.post(f"{BASE_URL}/prompts/refine", json={
        "Agent": {...},
        "Task": {...},
        "Prompt": {...}
    })
    refined_text = refine_response.json()["refined_prompt_text"]

# 4. Complete task
complete_response = requests.post(f"{BASE_URL}/tasks/complete", json={
    "task_id": task_id,
    "Agent": {...},
    "Task": {...},
    "Prompt": {...}  # Use refined prompt
})
outcomes = complete_response.json()["outcome"]["options"]
```

## 🎯 Pedagogical Approach

This system teaches the **Prompt → Output → Refine → Improved Output** cycle:

1. **Initial Attempt**: Students create their first prompt
2. **Feedback**: System provides immediate quality metrics and agent reactions
3. **Refinement**: Students iterate on their prompt using suggestions
4. **Results**: Better prompts lead to better outcomes, reinforcing learning

## 🏢 Department-Specific Tasks

The system supports various departments:

- **Marketing**: Email campaigns, social media, market research
- **Engineering**: Feature development, bug fixes, code reviews
- **Research**: Product research, competitive analysis, user studies
- **HR**: Workshops, training, recruitment
- **Design**: UI design, UX research, prototypes
- **Sales**: Sales pitches, client meetings, proposals
- **Operations**: Process optimization, resource planning, reporting

## 🔌 Integration with Unity

The API is designed to integrate with Unity games:

1. Use Unity's `UnityWebRequest` to call API endpoints
2. Parse JSON responses using Unity's `JsonUtility` or Newtonsoft.Json
3. Display agent feedback and outcomes in game UI
4. Update game stats based on outcome modifiers

## 📄 License

This project is part of the Game educational system.

## 🤝 Contributing

For questions or contributions, please contact the development team.

## 🐛 Troubleshooting

### OpenAI API Not Working

- Verify your API key is set correctly in `.env`
- Check your OpenAI account has credits
- Ensure you're using a supported model

### Port Already in Use

Change the port in `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8002)  # Use different port
```

### Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
