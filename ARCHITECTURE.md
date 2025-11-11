# System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Unity Game Client                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Management   │  │ Prompt       │  │ Outcome      │         │
│  │ Menu UI      │  │ Editor UI    │  │ Selection UI │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                   ┌────────▼────────┐                           │
│                   │  API Client     │                           │
│                   │  (C# Wrapper)   │                           │
│                   └────────┬────────┘                           │
└────────────────────────────┼──────────────────────────────────┘
                             │ HTTP/JSON
                             │
┌────────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend Server                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                      main.py                              │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │ │
│  │  │ /tasks/*   │  │ /prompts/* │  │ /health    │        │ │
│  │  │ Endpoints  │  │ Endpoints  │  │ Endpoints  │        │ │
│  │  └─────┬──────┘  └─────┬──────┘  └────────────┘        │ │
│  └────────┼───────────────┼──────────────────────────────────┘ │
│           │               │                                     │
│  ┌────────▼───────────────▼──────────────────────────────────┐ │
│  │                   Core Services                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │ Task         │  │ Prompt       │  │ Outcome      │   │ │
│  │  │ Manager      │  │ Evaluator    │  │ Generator    │   │ │
│  │  └──────────────┘  └──────┬───────┘  └──────┬───────┘   │ │
│  └───────────────────────────┼──────────────────┼───────────┘ │
│                              │                  │               │
│  ┌───────────────────────────▼──────────────────▼───────────┐ │
│  │              OpenAI Service Layer                         │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  • Async API calls                                  │  │ │
│  │  │  • JSON response parsing                            │  │ │
│  │  │  • Error handling & fallbacks                       │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────┬────────────────────────────────┘ │
└────────────────────────────────┼──────────────────────────────┘
                                 │ HTTPS
                                 │
                    ┌────────────▼────────────┐
                    │   OpenAI API            │
                    │   (gpt-4o-mini)         │
                    └─────────────────────────┘
```

## 📦 Component Architecture

```
Backend/agent-task-assignment/
│
├── 🎯 Entry Point
│   └── main.py
│       ├── FastAPI app initialization
│       ├── CORS middleware
│       ├── Lifespan management
│       └── Route definitions
│
├── ⚙️ Configuration
│   ├── config.py
│   │   └── Settings (Pydantic BaseSettings)
│   └── .env
│       └── Environment variables
│
├── 📊 Data Models (models/)
│   ├── agent.py
│   │   ├── Agent
│   │   ├── AgentStat
│   │   └── Department (Enum)
│   │
│   ├── task.py
│   │   ├── Task
│   │   ├── TaskAssignment
│   │   ├── TaskStatus (Enum)
│   │   └── TaskCategory (Enum)
│   │
│   ├── prompt.py
│   │   ├── Prompt
│   │   ├── PromptParameter
│   │   └── PromptParameterType (Enum)
│   │
│   ├── outcome.py
│   │   ├── TaskOutcome
│   │   ├── OutcomeOption
│   │   ├── OutcomeType (Enum)
│   │   └── StatModifier
│   │
│   ├── requests.py
│   │   ├── TaskAssignmentRequest
│   │   ├── PromptEvaluationRequest
│   │   ├── PromptRefinementRequest
│   │   └── TaskCompletionRequest
│   │
│   └── responses.py
│       ├── TaskAssignmentResponse
│       ├── PromptEvaluationResponse
│       ├── PromptRefinementResponse
│       ├── TaskCompletionResponse
│       ├── PromptQualityMetrics
│       ├── AgentFeedbackResponse
│       └── ErrorResponse
│
├── 🔧 Services (services/)
│   ├── openai_service.py
│   │   └── OpenAIService
│   │       ├── generate_completion()
│   │       ├── generate_json_completion()
│   │       └── validate_api_key()
│   │
│   ├── prompt_evaluator.py
│   │   └── PromptEvaluator
│   │       ├── calculate_base_scores()
│   │       ├── evaluate_prompt_with_ai()
│   │       └── suggest_refinements()
│   │
│   └── outcome_generator.py
│       └── OutcomeGenerator
│           ├── generate_outcomes()
│           ├── _determine_outcome_distribution()
│           └── _generate_fallback_options()
│
└── 💼 Core Logic (core/)
    └── task_manager.py
        └── TaskManager
            ├── create_task_assignment()
            ├── get_task()
            ├── update_task_status()
            ├── get_agent_tasks()
            └── get_pending_tasks()
```

## 🔄 Data Flow

### 1. Task Assignment Flow

```
User Action (Unity)
    │
    ├─→ Create TaskAssignmentRequest
    │   ├─ Agent data
    │   ├─ Task data
    │   └─ Initial Prompt
    │
    ▼
POST /tasks/assign
    │
    ├─→ Validate Request (Pydantic)
    │
    ├─→ TaskManager.create_task_assignment()
    │   ├─ Generate task_id
    │   ├─ Create TaskAssignment
    │   └─ Store in memory
    │
    ├─→ Generate initial feedback
    │
    └─→ Return TaskAssignmentResponse
        │
        ▼
    Update Unity UI
    ├─ Show task_id
    ├─ Display feedback
    └─ Enable prompt editing
```

### 2. Prompt Evaluation Flow

```
User Types Prompt (Unity)
    │
    ├─→ Debounce (500ms)
    │
    ├─→ Create PromptEvaluationRequest
    │
    ▼
POST /prompts/evaluate
    │
    ├─→ Validate Request
    │
    ├─→ PromptEvaluator.evaluate_prompt_with_ai()
    │   │
    │   ├─→ calculate_base_scores()
    │   │   ├─ Analyze text length
    │   │   ├─ Check personalization
    │   │   ├─ Calculate parameter scores
    │   │   └─ Compute agent fit
    │   │
    │   ├─→ OpenAIService.generate_json_completion()
    │   │   ├─ Build system prompt
    │   │   ├─ Build user prompt with context
    │   │   ├─ Call OpenAI API
    │   │   └─ Parse JSON response
    │   │
    │   └─→ Combine scores & feedback
    │
    └─→ Return PromptEvaluationResponse
        │
        ▼
    Update Unity UI (Real-time)
    ├─ Update quality bars
    ├─ Show agent emotion
    ├─ Display feedback text
    └─ List suggestions
```

### 3. Prompt Refinement Flow

```
User Clicks "Refine" (Unity)
    │
    ├─→ Create PromptRefinementRequest
    │   └─ Optional: focus_parameter
    │
    ▼
POST /prompts/refine
    │
    ├─→ Validate Request
    │
    ├─→ PromptEvaluator.suggest_refinements()
    │   │
    │   ├─→ OpenAIService.generate_json_completion()
    │   │   ├─ System: "You are a prompt engineering expert"
    │   │   ├─ User: Current prompt + context
    │   │   └─ Response: Refined text + improvements
    │   │
    │   └─→ Parse refinement suggestions
    │
    └─→ Return PromptRefinementResponse
        │
        ▼
    Update Unity UI
    ├─ Show refined prompt
    ├─ Highlight improvements
    └─ Allow user to accept/modify
```

### 4. Task Completion Flow

```
User Submits Final Prompt (Unity)
    │
    ├─→ Create TaskCompletionRequest
    │   ├─ task_id
    │   ├─ Agent
    │   ├─ Task
    │   └─ Final Prompt
    │
    ▼
POST /tasks/complete
    │
    ├─→ Validate Request
    │
    ├─→ Verify task exists
    │
    ├─→ PromptEvaluator.evaluate_prompt_with_ai()
    │   └─ Get final quality_score
    │
    ├─→ OutcomeGenerator.generate_outcomes()
    │   │
    │   ├─→ Determine outcome distribution
    │   │   └─ Based on quality_score
    │   │
    │   ├─→ OpenAIService.generate_json_completion()
    │   │   ├─ System: "Generate realistic outcomes"
    │   │   ├─ User: Task + Agent + Quality context
    │   │   └─ Response: 2-4 outcome options
    │   │
    │   └─→ Parse & structure outcomes
    │
    ├─→ TaskManager.update_task_status()
    │   └─ Mark as COMPLETED
    │
    └─→ Return TaskCompletionResponse
        │
        ▼
    Update Unity UI
    ├─ Show outcome options
    ├─ Display stat modifiers
    ├─ Show narrative text
    └─ Allow player to choose
        │
        ▼
    Apply chosen outcome to game state
```

## 🧩 Service Dependencies

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│                   (main.py)                     │
└────────┬────────────────────────────┬───────────┘
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│  TaskManager    │          │ PromptEvaluator │
│  (core/)        │          │ (services/)     │
└─────────────────┘          └────────┬────────┘
                                      │
                                      │ depends on
                                      ▼
                             ┌─────────────────┐
                             │ OpenAIService   │
                             │ (services/)     │
                             └────────┬────────┘
                                      │
                                      │ depends on
                                      ▼
                             ┌─────────────────┐
                             │ OutcomeGenerator│
                             │ (services/)     │
                             └────────┬────────┘
                                      │
                                      │ depends on
                                      ▼
                             ┌─────────────────┐
                             │ OpenAIService   │
                             └─────────────────┘
```

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────┐
│              Environment Variables               │
│  ┌───────────────────────────────────────────┐  │
│  │  OPENAI_API_KEY (from .env)               │  │
│  │  ├─ Never committed to git                │  │
│  │  ├─ Loaded at startup                     │  │
│  │  └─ Used by OpenAIService only            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              Configuration Layer                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Settings (Pydantic BaseSettings)         │  │
│  │  ├─ Type validation                       │  │
│  │  ├─ Default values                        │  │
│  │  └─ Environment variable mapping          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              Request Validation                  │
│  ┌───────────────────────────────────────────┐  │
│  │  Pydantic Models                          │  │
│  │  ├─ Type checking                         │  │
│  │  ├─ Range validation (1-10)               │  │
│  │  ├─ Length limits                         │  │
│  │  └─ Required field enforcement            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              CORS Middleware                     │
│  ┌───────────────────────────────────────────┐  │
│  │  ├─ Allow origins: * (dev)                │  │
│  │  ├─ Allow methods: *                      │  │
│  │  └─ Allow headers: *                      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📈 Scalability Considerations

### Current Architecture (Single Instance)
```
Unity Client → FastAPI Server → OpenAI API
     │              │
     │              └─→ In-Memory Task Storage
     │
     └─→ HTTP Requests (Synchronous from Unity perspective)
```

### Future Scalability (Production)
```
                    ┌─→ FastAPI Instance 1 ─┐
Unity Clients ─→ Load Balancer ─→ FastAPI Instance 2 ─┼─→ OpenAI API
                    └─→ FastAPI Instance N ─┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Redis/Database  │
                    │  (Shared State)  │
                    └──────────────────┘
```

## 🎯 Design Patterns Used

### 1. Service Layer Pattern
- Separation of business logic from API endpoints
- Services: OpenAIService, PromptEvaluator, OutcomeGenerator

### 2. Repository Pattern
- TaskManager acts as repository for task data
- Abstraction over data storage (currently in-memory)

### 3. Dependency Injection
- Services injected into endpoints via lifespan
- Loose coupling between components

### 4. Strategy Pattern
- Different evaluation strategies (AI vs. fallback)
- Different outcome generation strategies based on quality

### 5. Factory Pattern
- Dynamic outcome option generation
- Task assignment creation

## 🔄 State Management

```
Task Lifecycle:
┌─────────┐  assign   ┌────────────┐  start   ┌─────────────┐
│ PENDING │ ────────→ │ IN_PROGRESS│ ───────→ │  COMPLETED  │
└─────────┘           └────────────┘          └─────────────┘
                            │                         │
                            │ error                   │
                            ▼                         │
                      ┌─────────┐                     │
                      │ FAILED  │←────────────────────┘
                      └─────────┘
```

## 🧪 Testing Architecture

```
┌─────────────────────────────────────────────────┐
│              Test Suite (pytest)                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Unit Tests (test_models.py)              │  │
│  │  ├─ Model validation                      │  │
│  │  ├─ Enum values                           │  │
│  │  └─ Helper methods                        │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  Integration Tests (test_api.py)          │  │
│  │  ├─ Endpoint testing                      │  │
│  │  ├─ Request/response validation           │  │
│  │  └─ Error handling                        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📊 Performance Characteristics

### Response Times (Typical)
- Task Assignment: ~50ms (no AI)
- Prompt Evaluation: ~1-3s (with AI)
- Prompt Refinement: ~2-4s (with AI)
- Task Completion: ~2-5s (with AI)

### Bottlenecks
1. OpenAI API calls (network latency)
2. JSON parsing for large responses
3. In-memory storage (not persistent)

### Optimization Strategies
1. Async/await for non-blocking I/O
2. Debouncing for real-time evaluation
3. Caching for repeated evaluations
4. Fallback to rule-based when AI unavailable

---

This architecture provides a solid foundation for the Agent Task Assignment System with clear separation of concerns, scalability options, and maintainability.
