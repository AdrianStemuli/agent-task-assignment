from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_prompt_quality(prompt: str):
    """Fast model to score prompt quality."""

    response = await client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[
            {"role": "system", "content": "Return ONLY a number between 0 and 1 representing prompt quality."},
            {"role": "user", "content": prompt.Text}
        ],
    )
  
    score = float(response.choices[0].message.content.strip())
    return score


async def generate_agent_feedback(agent_name: str, task_title: str, prompt: str):
    response = await client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[
            {"role": "system", "content": "Provide short feedback from the agent about the prompt."},
            {"role": "user", "content": f"Agent: {agent_name}. Task: {task_title}. Prompt: {prompt}"}
        ],
    )

    return response.choices[0].message.content


async def generate_narrative(task_title: str, agent_name: str):
    response = await client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[
            {"role": "system", "content": "Return a short neutral narrative text."},
            {"role": "user", "content": f"Agent {agent_name} completed task '{task_title}'."}
        ],
    )

    return response.choices[0].message.content

