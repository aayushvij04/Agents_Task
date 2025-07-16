from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class SummaryAgentInput(BaseModel):
    user_msg: str
    preprocessor_output: Dict[str, Any]
    profile_delta: Dict[str, Any]
    prev_summary: Optional[str] = ""

class SummaryAgentOutput(BaseModel):
    summary: str
