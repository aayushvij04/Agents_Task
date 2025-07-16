from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

WorkerRoute = Literal["profile_gap", "clarifier", "explain", "practice", "support"]

class RouterInput(BaseModel):
    intent: str
    confidence: float
    emotion: str
    profile_delta: Dict[str, Any]
    conversation_summary: str

class RouterOutput(BaseModel):
    route: WorkerRoute
    reason: str
