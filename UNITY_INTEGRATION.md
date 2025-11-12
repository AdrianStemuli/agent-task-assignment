# Unity Integration Guide

This guide explains how to integrate the Agent Task Assignment API with your Unity game.

## Overview

The API provides endpoints for:
1. Assigning tasks to agents
2. Evaluating prompt quality in real-time
3. Getting AI-powered refinement suggestions
4. Generating outcomes based on prompt quality

## Key Features

### Agent Stats Impact
The API now considers agent stats when evaluating prompts and generating outcomes:

- **Expertise**: Improves clarity score (±25% based on expertise level)
- **Quality**: Enhances context understanding (±15% based on quality level)  
- **Reliability**: Affects tone interpretation (±10% based on reliability level)
- **Speed**: Influences task completion time in outcomes
- **Capacity**: Affects workload handling in outcomes
- **TokenMultiplier**: Amplifies outcome impact (higher multiplier = more significant results)

### Unity-Compatible Structure
The API supports the exact object structure used in your Unity game:

**Agent Example:**
```json
{
  "ID": "a77e98ce-2dc5-4abb-8e7f-e82c3cc1443c",
  "Name": "Analyst", 
  "Stats": [
    {"Name": "Expertise", "StatValueObj": 8},
    {"Name": "Speed", "StatValueObj": 6},
    {"Name": "Reliability", "StatValueObj": 8},
    {"Name": "Quality", "StatValueObj": 7},
    {"Name": "Capacity", "StatValueObj": 3},
    {"Name": "TokenMultiplier", "StatValueObj": 1.5}
  ]
}
```

**Task Example:**
```json
{
  "ID": "e84f8439-8072-4b02-85b0-44d0dad335b7",
  "Title": "Write email",
  "Description": "Write an email to Alice"
}
```

## Unity Setup

### 1. Install Dependencies

You'll need a JSON library for Unity. We recommend:
- **Newtonsoft.Json** (Json.NET) - Available via Unity Package Manager or NuGet

### 2. API Configuration

Create a configuration ScriptableObject:

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "APIConfig", menuName = "Game/API Config")]
public class APIConfig : ScriptableObject
{
    public string baseUrl = "http://localhost:8001";
    public float requestTimeout = 30f;
}
```

### 3. API Client

Create an API client to handle requests:

```csharp
using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class TaskAssignmentAPIClient : MonoBehaviour
{
    [SerializeField] private APIConfig config;
    
    private string BaseUrl => config.baseUrl;
    
    // Assign a task
    public IEnumerator AssignTask(TaskAssignmentRequest request, Action<TaskAssignmentResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BaseUrl}/tasks/assign";
        string jsonData = JsonConvert.SerializeObject(request);
        
        using (UnityWebRequest www = CreatePostRequest(url, jsonData))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<TaskAssignmentResponse>(www.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                onError?.Invoke(www.error);
            }
        }
    }
    
    // Evaluate prompt quality
    public IEnumerator EvaluatePrompt(PromptEvaluationRequest request, Action<PromptEvaluationResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BaseUrl}/prompts/evaluate";
        string jsonData = JsonConvert.SerializeObject(request);
        
        using (UnityWebRequest www = CreatePostRequest(url, jsonData))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<PromptEvaluationResponse>(www.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                onError?.Invoke(www.error);
            }
        }
    }
    
    // Refine prompt
    public IEnumerator RefinePrompt(PromptRefinementRequest request, Action<PromptRefinementResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BaseUrl}/prompts/refine";
        string jsonData = JsonConvert.SerializeObject(request);
        
        using (UnityWebRequest www = CreatePostRequest(url, jsonData))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<PromptRefinementResponse>(www.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                onError?.Invoke(www.error);
            }
        }
    }
    
    // Complete task
    public IEnumerator CompleteTask(TaskCompletionRequest request, Action<TaskCompletionResponse> onSuccess, Action<string> onError)
    {
        string url = $"{BaseUrl}/tasks/complete";
        string jsonData = JsonConvert.SerializeObject(request);
        
        using (UnityWebRequest www = CreatePostRequest(url, jsonData))
        {
            yield return www.SendWebRequest();
            
            if (www.result == UnityWebRequest.Result.Success)
            {
                var response = JsonConvert.DeserializeObject<TaskCompletionResponse>(www.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else
            {
                onError?.Invoke(www.error);
            }
        }
    }
    
    private UnityWebRequest CreatePostRequest(string url, string jsonData)
    {
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        UnityWebRequest www = new UnityWebRequest(url, "POST");
        www.uploadHandler = new UploadHandlerRaw(bodyRaw);
        www.downloadHandler = new DownloadHandlerBuffer();
        www.SetRequestHeader("Content-Type", "application/json");
        www.timeout = (int)config.requestTimeout;
        return www;
    }
}
```

### 4. Data Models

Create C# classes matching the API models:

```csharp
using System;
using System.Collections.Generic;

[Serializable]
public class Agent
{
    public string ID;  // UUID from Unity
    public string Name;
    public List<AgentStat> Stats;
    
    // Optional fields for backward compatibility
    public string Department = "Research";
    public string preferred_tone = "balanced";
    public int autonomy_preference = 5;
}

[Serializable]
public class AgentStat
{
    public string Name;
    public float StatValueObj;  // Changed from Value to StatValueObj, supports float for TokenMultiplier
}

[Serializable]
public class Task
{
    public string ID;  // UUID from Unity
    public string Title;
    public string Description;
    
    // Optional field for backward compatibility
    public string Category = "custom";
}

[Serializable]
public class Prompt
{
    public string Text;
    public List<PromptParameter> Parameters = new List<PromptParameter>();
}

[Serializable]
public class PromptParameter
{
    public string Name;
    public int Value;
}

// Request Models
[Serializable]
public class TaskAssignmentRequest
{
    public Agent Agent;
    public Task Task;
    public Prompt Prompt;
}

[Serializable]
public class PromptEvaluationRequest
{
    public Agent Agent;
    public Task Task;
    public Prompt Prompt;
}

[Serializable]
public class PromptRefinementRequest
{
    public Agent Agent;
    public Task Task;
    public Prompt Prompt;
    public string focus_parameter;
}

[Serializable]
public class TaskCompletionRequest
{
    public string task_id;
    public Agent Agent;
    public Task Task;
    public Prompt Prompt;
}

// Response Models
[Serializable]
public class TaskAssignmentResponse
{
    public bool success;
    public TaskAssignment task_assignment;
    public string initial_feedback;
    public string message;
}

[Serializable]
public class TaskAssignment
{
    public string task_id;
    public string agent_name;
    public Task task;
    public string status;
}

[Serializable]
public class PromptEvaluationResponse
{
    public bool success;
    public PromptQualityMetrics quality_metrics;
    public AgentFeedbackResponse agent_feedback;
    public List<string> suggestions;
    public bool is_ready;
    public string message;
}

[Serializable]
public class PromptQualityMetrics
{
    public float overall_score;
    public float clarity_score;
    public float context_score;
    public float tone_score;
    public float agency_score;
    public float empathy_score;
    public float agent_fit_score;
}

[Serializable]
public class AgentFeedbackResponse
{
    public string emotion;
    public string feedback_text;
    public string visual_indicator;
}

[Serializable]
public class PromptRefinementResponse
{
    public bool success;
    public string refined_prompt_text;
    public Dictionary<string, string> improvements;
    public float expected_quality_improvement;
    public string message;
}

[Serializable]
public class TaskCompletionResponse
{
    public bool success;
    public TaskOutcome outcome;
    public string message;
}

[Serializable]
public class TaskOutcome
{
    public string task_id;
    public string agent_name;
    public float prompt_quality_score;
    public List<OutcomeOption> options;
    public string agent_feedback;
}

[Serializable]
public class OutcomeOption
{
    public string option_id;
    public string title;
    public string description;
    public string outcome_type;
    public List<StatModifier> stat_modifiers;
    public string narrative_text;
}

[Serializable]
public class StatModifier
{
    public string stat_name;
    public int change;
    public bool percentage;
}
```

## Example Usage in Unity

### Task Assignment Flow

```csharp
using UnityEngine;
using System.Collections;

public class TaskAssignmentManager : MonoBehaviour
{
    [SerializeField] private TaskAssignmentAPIClient apiClient;
    
    private Agent currentAgent;
    private Task currentTask;
    private string currentTaskId;
    
    public void StartTaskAssignment(Agent agent, Task task)
    {
        currentAgent = agent;
        currentTask = task;
        
        // Create initial prompt
        Prompt initialPrompt = new Prompt
        {
            Text = "Complete this task",
            Parameters = new List<PromptParameter>()
        };
        
        // Show prompt editing UI
        ShowPromptEditor(initialPrompt);
    }
    
    public void OnPromptChanged(string promptText, List<PromptParameter> parameters)
    {
        Prompt prompt = new Prompt
        {
            Text = promptText,
            Parameters = parameters
        };
        
        // Evaluate in real-time
        StartCoroutine(EvaluateAndShowFeedback(prompt));
    }
    
    private IEnumerator EvaluateAndShowFeedback(Prompt prompt)
    {
        var request = new PromptEvaluationRequest
        {
            Agent = currentAgent,
            Task = currentTask,
            Prompt = prompt
        };
        
        yield return apiClient.EvaluatePrompt(
            request,
            onSuccess: (response) =>
            {
                // Update UI with quality metrics
                UpdateQualityUI(response.quality_metrics);
                
                // Show agent reaction
                ShowAgentReaction(response.agent_feedback);
                
                // Display suggestions
                ShowSuggestions(response.suggestions);
            },
            onError: (error) =>
            {
                Debug.LogError($"Evaluation failed: {error}");
            }
        );
    }
    
    public void OnSubmitPrompt(Prompt finalPrompt)
    {
        // First assign the task
        var assignRequest = new TaskAssignmentRequest
        {
            Agent = currentAgent,
            Task = currentTask,
            Prompt = finalPrompt
        };
        
        StartCoroutine(AssignAndCompleteTask(assignRequest, finalPrompt));
    }
    
    private IEnumerator AssignAndCompleteTask(TaskAssignmentRequest assignRequest, Prompt finalPrompt)
    {
        // Assign task
        yield return apiClient.AssignTask(
            assignRequest,
            onSuccess: (assignResponse) =>
            {
                currentTaskId = assignResponse.task_assignment.task_id;
                Debug.Log($"Task assigned: {currentTaskId}");
                
                // Show agent working animation
                ShowAgentWorking();
                
                // Complete task after delay
                StartCoroutine(CompleteTaskAfterDelay(finalPrompt, 2f));
            },
            onError: (error) =>
            {
                Debug.LogError($"Assignment failed: {error}");
            }
        );
    }
    
    private IEnumerator CompleteTaskAfterDelay(Prompt finalPrompt, float delay)
    {
        yield return new WaitForSeconds(delay);
        
        var completeRequest = new TaskCompletionRequest
        {
            task_id = currentTaskId,
            Agent = currentAgent,
            Task = currentTask,
            Prompt = finalPrompt
        };
        
        yield return apiClient.CompleteTask(
            completeRequest,
            onSuccess: (response) =>
            {
                // Show outcome options to player
                ShowOutcomeOptions(response.outcome);
            },
            onError: (error) =>
            {
                Debug.LogError($"Completion failed: {error}");
            }
        );
    }
    
    private void UpdateQualityUI(PromptQualityMetrics metrics)
    {
        // Update UI elements showing quality scores
        // e.g., progress bars, color indicators, etc.
    }
    
    private void ShowAgentReaction(AgentFeedbackResponse feedback)
    {
        // Display agent emotion/reaction in game world
        // e.g., show emote, play animation, display speech bubble
    }
    
    private void ShowSuggestions(List<string> suggestions)
    {
        // Display suggestions in UI
    }
    
    private void ShowPromptEditor(Prompt prompt)
    {
        // Show UI for editing prompt
    }
    
    private void ShowAgentWorking()
    {
        // Show agent working animation
    }
    
    private void ShowOutcomeOptions(TaskOutcome outcome)
    {
        // Display outcome options for player to choose
        // Apply stat modifiers based on player's choice
    }
}
```

### UI Integration Example

```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class PromptEditorUI : MonoBehaviour
{
    [SerializeField] private TMP_InputField promptInputField;
    [SerializeField] private Slider claritySlider;
    [SerializeField] private Slider contextSlider;
    [SerializeField] private Slider toneSlider;
    [SerializeField] private Slider agencySlider;
    [SerializeField] private Slider empathySlider;
    
    [SerializeField] private Image qualityIndicator;
    [SerializeField] private TMP_Text agentFeedbackText;
    [SerializeField] private GameObject agentEmoteContainer;
    
    [SerializeField] private TaskAssignmentManager taskManager;
    
    private void Start()
    {
        // Add listeners
        promptInputField.onValueChanged.AddListener(OnPromptTextChanged);
        claritySlider.onValueChanged.AddListener(_ => OnParameterChanged());
        contextSlider.onValueChanged.AddListener(_ => OnParameterChanged());
        toneSlider.onValueChanged.AddListener(_ => OnParameterChanged());
        agencySlider.onValueChanged.AddListener(_ => OnParameterChanged());
        empathySlider.onValueChanged.AddListener(_ => OnParameterChanged());
    }
    
    private void OnPromptTextChanged(string text)
    {
        OnParameterChanged();
    }
    
    private void OnParameterChanged()
    {
        // Debounce and trigger evaluation
        CancelInvoke(nameof(TriggerEvaluation));
        Invoke(nameof(TriggerEvaluation), 0.5f);
    }
    
    private void TriggerEvaluation()
    {
        var parameters = new List<PromptParameter>
        {
            new PromptParameter { Name = "Clarity", Value = (int)claritySlider.value },
            new PromptParameter { Name = "Context", Value = (int)contextSlider.value },
            new PromptParameter { Name = "Tone", Value = (int)toneSlider.value },
            new PromptParameter { Name = "Agency", Value = (int)agencySlider.value },
            new PromptParameter { Name = "Empathy", Value = (int)empathySlider.value }
        };
        
        taskManager.OnPromptChanged(promptInputField.text, parameters);
    }
    {
        // Update color based on score
        if (score >= 0.8f)
            qualityIndicator.color = Color.green;
        else if (score >= 0.6f)
            qualityIndicator.color = Color.yellow;
        else
            qualityIndicator.color = Color.red;
    }
    
    public void ShowAgentFeedback(string emotion, string feedback)
    {
        agentFeedbackText.text = feedback;
        // Show appropriate emote based on emotion
    }
}
```

## Best Practices

1. **Caching**: Cache agent and task data to minimize API calls
2. **Error Handling**: Always handle network errors gracefully
3. **Loading States**: Show loading indicators during API calls
4. **Debouncing**: Debounce real-time evaluation to avoid too many requests
5. **Offline Mode**: Consider implementing a fallback for offline play

## Performance Tips

- Use object pooling for UI elements
- Implement request queuing for multiple simultaneous tasks
- Cache API responses when appropriate
- Use coroutines efficiently to avoid blocking the main thread

## Troubleshooting

### Connection Issues
- Ensure the API server is running
- Check firewall settings
- Verify the correct base URL in APIConfig

### JSON Parsing Errors
- Ensure Newtonsoft.Json is properly installed
- Check that model classes match API response structure

### Timeout Issues
- Increase `requestTimeout` in APIConfig
- Check network connectivity
- Verify OpenAI API is responding (if using AI features)

## Example Game Flow

1. **Player opens management menu** → Shows available agents and tasks
2. **Player selects agent and task** → Opens prompt editor
3. **Player types prompt** → Real-time evaluation shows quality metrics
4. **Agent reacts in game world** → Shows emotion based on prompt quality
5. **Player refines prompt** → Uses AI suggestions or manual editing
6. **Player submits final prompt** → Task is assigned
7. **Agent works on task** → Visual feedback in game world
8. **Task completes** → Player chooses from outcome options
9. **Stats are updated** → Game state reflects chosen outcome

## Additional Resources

- API Documentation: http://localhost:8001/docs
- Example Postman Collection: `postman_collection.json`
- Python Example: `example_usage.py`
