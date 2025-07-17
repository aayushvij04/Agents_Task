from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any

class LTMProfile(BaseModel):
    learning_style: Optional[str] = None
    motivation_type: Optional[str] = None
    goals: List[str] = []
    mastered_topics: List[str] = []
    struggling_topics: List[str] = []
    emotion_baseline: Optional[str] = None
    performance_history: Dict[str, float] = {}

class STMPreprocessorOutput(BaseModel):
    emotion: Optional[str] = None
    intent: Optional[str] = None
    topic_primary: Optional[str] = None
    confidence: Optional[float] = None

class STMPerformanceData(RootModel[Dict[str, float]]):
    pass

class STMTurn(BaseModel):
    turn: int
    user_msg: Optional[str] = None
    bot_reply: Optional[str] = None
    preprocessor_output: Optional[STMPreprocessorOutput] = None
    worker_agent: Optional[str] = None
    performance_data: Optional[Dict[str, float]] = None

class LTMConsolidationInput(BaseModel):
    student_id: str
    current_ltm_profile: LTMProfile
    short_term_memory: List[STMTurn]

class LTMUpdateOperation(BaseModel):
    operation: str
    field: Optional[str] = None
    value: Optional[Any] = None
    evidence: Optional[str] = None
    text_to_embed: Optional[str] = None

class LTMConsolidationOutput(BaseModel):
    student_id: str
    rationale: str
    updates: List[LTMUpdateOperation]

LTM_ENUMS = {
    "learning_style": ["visual", "textual", "practice_oriented"],
    "emotion": ["joy", "sadness", "anger", "fear", "surprise", "love", "neutral", "uncertain"],
    "intent": [
        "ask_explanation", "request_example", "request_practice", "answer_submission",
        "ask_solution_check", "ask_hint", "emotional_support", "request_motivation",
        "feedback_positive", "feedback_negative", "meta_platform", "greeting", "chit_chat"
    ],
    "topic": [
        "fractions", "decimals_percentages", "geometry", "algebra_linear",
        "algebra_quadratic", "statistics", "probability_basic", "trigonometry_basic"
    ]
} 