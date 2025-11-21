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

class Focus(BaseModel):
    Name: str
    Value: float


class RequestBodyRefine(BaseModel):
    Agent: Agent
    Task: Task
    Prompt: str
    focus_parameter: List[Focus]

class RequestBodyGenerate(BaseModel):
    Task: Task
    Agent: Agent
    style_preference: str