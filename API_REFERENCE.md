# API Reference

Complete reference for all Agent Task Assignment System endpoints.

**Base URL**: `http://localhost:8001`

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [Task Management](#task-management)
- [Prompt Engineering](#prompt-engineering)
- [System](#system)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

---

## Authentication

Currently, no authentication is required. In production, consider adding API keys or JWT tokens.

---

## Task Management

### Assign Task

Create a new task assignment with an initial prompt.

**Endpoint**: `POST /tasks/assign`

**Request Body**:
```json
{
  "Agent": {
    "Name": "string",
    "Department": "Research|Marketing|Engineering|HR|Sales|Design|Operations",
    "Stats": [
      {"Name": "Expertise", "Value": 1-10},
      {"Name": "Quality", "Value": 1-10},
      {"Name": "Reliability", "Value": 1-10},
      {"Name": "Speed", "Value": 1-10},
      {"Name": "Capacity", "Value": 1-10}
    ],
    "preferred_tone": "string (optional)",
    "autonomy_preference": 1-10 (optional)
  },
  "Task": {
    "Title": "string (max 100 chars)",
    "Description": "string (max 500 chars)",
    "Category": "string (optional)"
  },
  "Prompt": {
    "Text": "string (max 2000 chars)",
    "Parameters": [
      {"Name": "Clarity|Context|Tone|Agency|Empathy", "Value": 1-10}
    ]
  }
}
```

**Response**: `201 Created`
```json
{
  "success": true,
  "task_assignment": {
    "task_id": "task_abc123",
    "agent_name": "Bob",
    "task": {
      "Title": "Write email campaign",
      "Description": "Write an email campaign..."
    },
    "status": "pending",
    "assigned_at": "2025-11-11T10:00:00Z"
  },
  "initial_feedback": "Bob has received the task...",
  "message": "Task successfully assigned to Bob"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8001/tasks/assign" \
  -H "Content-Type: application/json" \
  -d @task_assignment.json
```

---

### Complete Task

Mark a task as complete and generate outcome options.

**Endpoint**: `POST /tasks/complete`

**Request Body**:
```json
{
  "task_id": "task_abc123",
  "Agent": { /* Same as assign */ },
  "Task": { /* Same as assign */ },
  "Prompt": { /* Final refined prompt */ }
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "outcome": {
    "task_id": "task_abc123",
    "agent_name": "Bob",
    "prompt_quality_score": 0.85,
    "options": [
      {
        "option_id": "outcome_1",
        "title": "Excellent Email Campaign",
        "description": "Bob created a highly engaging campaign...",
        "outcome_type": "buff",
        "stat_modifiers": [
          {
            "stat_name": "Customer Retention",
            "change": 15,
            "percentage": true
          }
        ],
        "narrative_text": "The campaign resonated well..."
      }
    ],
    "agent_feedback": "Great prompt! Clear direction helped..."
  },
  "message": "Task completed successfully"
}
```

---

### Get Task

Retrieve details of a specific task.

**Endpoint**: `GET /tasks/{task_id}`

**Parameters**:
- `task_id` (path): Task identifier

**Response**: `200 OK`
```json
{
  "task_id": "task_abc123",
  "agent_name": "Bob",
  "task": { /* Task details */ },
  "status": "pending|in_progress|completed|failed",
  "assigned_at": "2025-11-11T10:00:00Z",
  "completed_at": "2025-11-11T10:30:00Z"
}
```

**Errors**:
- `404 Not Found`: Task doesn't exist

---

### List All Tasks

Get a list of all task assignments.

**Endpoint**: `GET /tasks`

**Response**: `200 OK`
```json
{
  "tasks": [ /* Array of task assignments */ ],
  "total": 10,
  "pending": 3
}
```

---

### Get Agent Tasks

Get all tasks assigned to a specific agent.

**Endpoint**: `GET /agents/{agent_name}/tasks`

**Parameters**:
- `agent_name` (path): Name of the agent

**Response**: `200 OK`
```json
{
  "agent_name": "Bob",
  "tasks": [ /* Array of task assignments */ ],
  "total": 5
}
```

---

## Prompt Engineering

### Evaluate Prompt

Evaluate prompt quality and get real-time feedback.

**Endpoint**: `POST /prompts/evaluate`

**Request Body**:
```json
{
  "Agent": { /* Agent details */ },
  "Task": { /* Task details */ },
  "Prompt": { /* Prompt to evaluate */ }
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "quality_metrics": {
    "overall_score": 0.75,
    "clarity_score": 0.8,
    "context_score": 0.7,
    "tone_score": 0.8,
    "agency_score": 0.7,
    "empathy_score": 0.6,
    "agent_fit_score": 0.85
  },
  "agent_feedback": {
    "emotion": "motivated",
    "feedback_text": "Good prompt! I have a clear understanding...",
    "visual_indicator": "thumbs_up"
  },
  "suggestions": [
    "Consider adding more context about the target audience",
    "You could specify the desired tone for the email"
  ],
  "is_ready": true,
  "message": "Prompt evaluation completed"
}
```

**Errors**:
- `503 Service Unavailable`: OpenAI not configured

**Quality Score Ranges**:
- `0.9-1.0`: Excellent
- `0.8-0.9`: Great
- `0.7-0.8`: Good
- `0.6-0.7`: Adequate
- `0.5-0.6`: Fair
- `<0.5`: Poor

**Agent Emotions**:
- `motivated`: Very positive
- `excited`: Enthusiastic
- `ready`: Prepared
- `neutral`: Okay
- `uncertain`: Needs clarity
- `confused`: Unclear
- `overwhelmed`: Too much/complex

**Visual Indicators**:
- `thumbs_up`: Positive
- `star`: Excellent
- `check`: Good
- `neutral`: Okay
- `question_mark`: Unclear
- `warning`: Issues

---

### Refine Prompt

Get AI-powered suggestions to improve a prompt.

**Endpoint**: `POST /prompts/refine`

**Request Body**:
```json
{
  "Agent": { /* Agent details */ },
  "Task": { /* Task details */ },
  "Prompt": { /* Current prompt */ },
  "focus_parameter": "Clarity" // Optional: Clarity|Context|Tone|Agency|Empathy
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "refined_prompt_text": "Hey Bob! I want you to write an email campaign...",
  "improvements": {
    "Clarity": "Added specific elements to include",
    "Context": "Specified the time period and target",
    "Agency": "Gave freedom for creativity on subject line"
  },
  "expected_quality_improvement": 0.25,
  "message": "Prompt refinement suggestions generated"
}
```

**Errors**:
- `503 Service Unavailable`: OpenAI not configured

---

## System

### Health Check (Simple)

Basic health check endpoint.

**Endpoint**: `GET /`

**Response**: `200 OK`
```json
{
  "message": "Agent Task Assignment System",
  "status": "active",
  "version": "1.0.0",
  "openai_enabled": true
}
```

---

### Health Check (Detailed)

Detailed system health information.

**Endpoint**: `GET /health`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "openai_configured": true,
  "openai_model": "gpt-4o-mini",
  "active_tasks": 10,
  "pending_tasks": 3
}
```

---

## Data Models

### Agent

```typescript
{
  Name: string,
  Department: "Research" | "Marketing" | "Engineering" | "HR" | "Sales" | "Design" | "Operations",
  Stats: AgentStat[5], // Exactly 5 stats required
  preferred_tone?: string, // Default: "balanced"
  autonomy_preference?: number // 1-10, Default: 5
}
```

### AgentStat

```typescript
{
  Name: "Expertise" | "Quality" | "Reliability" | "Speed" | "Capacity",
  Value: number // 1-10
}
```

### Task

```typescript
{
  Title: string, // Max 100 chars
  Description: string, // Max 500 chars
  Category?: TaskCategory
}
```

### TaskCategory

```
email_campaign, social_media, market_research,
workshop, training, recruitment,
feature_development, bug_fix, code_review,
product_research, competitive_analysis, user_study,
ui_design, ux_research, prototype,
sales_pitch, client_meeting, proposal,
process_optimization, resource_planning, reporting,
custom
```

### Prompt

```typescript
{
  Text: string, // Max 2000 chars
  Parameters: PromptParameter[]
}
```

### PromptParameter

```typescript
{
  Name: "Clarity" | "Context" | "Tone" | "Agency" | "Empathy",
  Value: number // 1-10
}
```

**Parameter Meanings**:
- **Clarity**: 1 (Vague) → 10 (Precise)
- **Context**: 1 (Minimal) → 10 (Rich)
- **Tone**: 1 (Directive) → 10 (Empowering)
- **Agency**: 1 (Strict Direction) → 10 (Freedom)
- **Empathy**: 1 (None) → 10 (High)

### OutcomeOption

```typescript
{
  option_id: string,
  title: string,
  description: string,
  outcome_type: "buff" | "debuff" | "neutral",
  stat_modifiers: StatModifier[],
  narrative_text: string
}
```

### StatModifier

```typescript
{
  stat_name: string, // e.g., "Revenue", "Morale", "Productivity"
  change: number, // Can be negative
  percentage: boolean // true = percentage, false = absolute
}
```

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional error details (optional)"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: External service unavailable

### Common Errors

**Validation Error (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "Agent", "Stats", 0, "Value"],
      "msg": "ensure this value is less than or equal to 10",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Not Found (404)**:
```json
{
  "detail": "Task task_abc123 not found"
}
```

**Service Unavailable (503)**:
```json
{
  "detail": "OpenAI service not configured. Set OPENAI_API_KEY environment variable."
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Consider implementing rate limiting per IP/user
- Use Redis for distributed rate limiting
- Set appropriate limits based on OpenAI API quotas

---

## Best Practices

### 1. Request Optimization

**Debounce real-time evaluation**:
```javascript
// Wait 500ms after user stops typing
let debounceTimer;
function onPromptChange(prompt) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    evaluatePrompt(prompt);
  }, 500);
}
```

### 2. Error Handling

**Always handle errors gracefully**:
```javascript
try {
  const response = await fetch('/prompts/evaluate', {
    method: 'POST',
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  const data = await response.json();
  // Handle success
} catch (error) {
  // Show user-friendly error message
  console.error('Evaluation failed:', error);
}
```

### 3. Caching

**Cache agent and task data**:
```javascript
// Cache agent data to avoid repeated requests
const agentCache = new Map();

function getAgent(name) {
  if (!agentCache.has(name)) {
    agentCache.set(name, fetchAgent(name));
  }
  return agentCache.get(name);
}
```

### 4. Loading States

**Show loading indicators**:
```javascript
setLoading(true);
try {
  const result = await evaluatePrompt(prompt);
  updateUI(result);
} finally {
  setLoading(false);
}
```

---

## Examples

### Complete Workflow

```javascript
// 1. Assign Task
const assignResponse = await fetch('/tasks/assign', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    Agent: { /* ... */ },
    Task: { /* ... */ },
    Prompt: { /* ... */ }
  })
});
const {task_assignment} = await assignResponse.json();

// 2. Evaluate Prompt (real-time)
const evalResponse = await fetch('/prompts/evaluate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    Agent: { /* ... */ },
    Task: { /* ... */ },
    Prompt: { /* updated prompt */ }
  })
});
const {quality_metrics, agent_feedback} = await evalResponse.json();

// 3. Refine if needed
if (quality_metrics.overall_score < 0.7) {
  const refineResponse = await fetch('/prompts/refine', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      Agent: { /* ... */ },
      Task: { /* ... */ },
      Prompt: { /* current prompt */ }
    })
  });
  const {refined_prompt_text} = await refineResponse.json();
  // Use refined prompt
}

// 4. Complete Task
const completeResponse = await fetch('/tasks/complete', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    task_id: task_assignment.task_id,
    Agent: { /* ... */ },
    Task: { /* ... */ },
    Prompt: { /* final prompt */ }
  })
});
const {outcome} = await completeResponse.json();

// 5. Present outcome options to player
outcome.options.forEach(option => {
  console.log(`${option.title}: ${option.description}`);
  option.stat_modifiers.forEach(mod => {
    console.log(`  ${mod.stat_name}: ${mod.change}${mod.percentage ? '%' : ''}`);
  });
});
```

---

## Interactive API Documentation

For interactive testing and detailed schemas:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## Support

For issues or questions:
1. Check this API reference
2. Review the main README.md
3. Test with Postman collection
4. Check server logs for errors
5. Contact development team
