from pydantic import BaseModel
from typing import List, Optional
class Stat(BaseModel):
    Name: str
    StatValueObj: float

class Agent(BaseModel):
    ID: str
    Name: str
    Stats: List[Stat]

class Task(BaseModel):
    Description: str
    ID: str
    Title: str

class RequestBody(BaseModel):
    Agent: Agent
    Task: Task
    Prompt: str