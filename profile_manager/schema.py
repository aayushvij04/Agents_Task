from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ProfileManagerInput(BaseModel):
    user_msg: str
    updated_summary: str
    current_profile: Dict[str, Any]

class NewFacts(BaseModel):
    recent_topic: Optional[str] = None
    emotion_trend: Optional[List[str]] = None
    confident_in: Optional[List[str]] = None

class ProfileManagerOutput(BaseModel):
    new_facts: Optional[Dict[str, Any]] = None
    profile_gaps: Optional[List[str]] = None
