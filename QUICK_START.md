# Quick Start Guide

Get the Agent Task Assignment System running in 5 minutes!

## 🚀 Installation

### Option 1: Using the run script (Recommended)

```bash
cd Backend/agent-task-assignment
./run.sh
```

The script will:
- Create a virtual environment
- Install dependencies
- Check for configuration
- Start the server

### Option 2: Manual setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the server
python main.py
```

## 🔑 Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

## 📚 Access the API

Once running:
- **API Server**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc

## 🎯 Try It Out

### Using the Interactive Docs (Easiest)

1. Open http://localhost:8001/docs
2. Click on "POST /tasks/assign"
3. Click "Try it out"
4. Use the example request or modify it
5. Click "Execute"

### Using cURL

```bash
# Assign a task
curl -X POST "http://localhost:8001/tasks/assign" \
  -H "Content-Type: application/json" \
  -d '{
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
        {"Name": "Clarity", "Value": 5}
      ]
    }
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8001/tasks/assign",
    json={
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
            "Description": "Write an email campaign"
        },
        "Prompt": {
            "Text": "Write an email to customers",
            "Parameters": []
        }
    }
)

print(response.json())
```

### Run the Example Script

```bash
python example_usage.py
```

This demonstrates the complete workflow:
1. Assign a task
2. Evaluate prompt quality
3. Refine the prompt
4. Complete task and generate outcomes

## 🎮 Complete Workflow Example

### 1. Assign Task
```bash
POST /tasks/assign
```
Returns: `task_id`, initial feedback

### 2. Evaluate Prompt (Real-time)
```bash
POST /prompts/evaluate
```
Returns: Quality scores, agent feedback, suggestions

### 3. Refine Prompt (Optional)
```bash
POST /prompts/refine
```
Returns: Improved prompt text, explanations

### 4. Complete Task
```bash
POST /tasks/complete
```
Returns: 2-4 outcome options with stat modifiers

## 🎓 Understanding Prompt Parameters

| Parameter | Low (1-3) | Medium (4-7) | High (8-10) |
|-----------|-----------|--------------|-------------|
| **Clarity** | Vague instructions | Some detail | Very specific |
| **Context** | No background | Some context | Rich context |
| **Tone** | Commanding | Balanced | Empowering |
| **Agency** | Strict direction | Guided | Full freedom |
| **Empathy** | Impersonal | Considerate | Highly empathetic |

## 📊 Quality Score Interpretation

- **0.9-1.0**: Excellent - Perfect prompt engineering
- **0.8-0.9**: Great - Very effective communication
- **0.7-0.8**: Good - Solid prompt with minor improvements possible
- **0.6-0.7**: Adequate - Gets the job done but could be better
- **0.5-0.6**: Fair - Needs improvement
- **Below 0.5**: Poor - Significant issues

## 🎁 Outcome Quality

Better prompts = Better outcomes!

- **High quality (0.8+)**: All positive outcomes (buffs)
- **Good quality (0.7-0.8)**: Mostly positive outcomes
- **Medium quality (0.5-0.7)**: Mixed outcomes
- **Low quality (0.3-0.5)**: Mostly negative outcomes
- **Poor quality (<0.3)**: All negative outcomes (debuffs)

## 🔧 Configuration

Edit `.env` to customize:

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

Run specific tests:

```bash
pytest tests/test_models.py
pytest tests/test_api.py
```

## 📱 Import Postman Collection

1. Open Postman
2. Click "Import"
3. Select `postman_collection.json`
4. Start testing!

## 🎮 Unity Integration

See `UNITY_INTEGRATION.md` for complete Unity integration guide with:
- C# API client
- Data models
- Example usage
- UI integration

## ❓ Troubleshooting

### "OpenAI API key is required"
- Add your API key to `.env` file
- Restart the server

### "Port 8001 already in use"
- Change port in `main.py`: `uvicorn.run(app, port=8002)`
- Or kill the process using port 8001

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### API returns 503 for OpenAI endpoints
- Check your OpenAI API key is valid
- Verify you have credits in your OpenAI account
- Check internet connectivity

## 📖 Next Steps

1. ✅ Get the API running
2. ✅ Try the example endpoints
3. ✅ Run `example_usage.py`
4. ✅ Integrate with Unity (see `UNITY_INTEGRATION.md`)
5. ✅ Customize for your game

## 💡 Tips

- Start with simple prompts and iterate
- Use the real-time evaluation to learn
- Pay attention to agent feedback
- Experiment with different parameter combinations
- Better prompts lead to better outcomes!

## 📚 Documentation

- **Full README**: `README.md`
- **Unity Integration**: `UNITY_INTEGRATION.md`
- **API Docs**: http://localhost:8001/docs
- **Example Code**: `example_usage.py`
- **Postman Collection**: `postman_collection.json`

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the full README
3. Check API documentation
4. Contact the development team

---

**Happy Prompting! 🚀**
