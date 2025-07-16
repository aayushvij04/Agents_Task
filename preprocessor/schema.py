from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from uuid import UUID
from datetime import datetime

Language = Literal["en", "hi", "en-IN"]
Emotion = Literal["joy", "sadness", "anger", "fear", "surprise", "love", "neutral", "uncertain"]
Intent = Literal[
    "ask_explanation", "request_example", "request_practice", "answer_submission",
    "ask_solution_check", "ask_hint", "emotional_support", "request_motivation",
    "feedback_positive", "feedback_negative", "meta_platform", "greeting", "chit_chat"
]
Topic = Literal[
    "fractions", "decimals_percentages", "geometry", "algebra_linear",
    "algebra_quadratic", "statistics", "probability_basic", "trigonometry_basic"
]

class PreProcessorInput(BaseModel):
    user_msg: str
    conversation_summary: str

class Rationale(BaseModel):
    lang_reason: str
    emotion_reason: str
    intent_reason: str
    topic_reason: str
    history_shift: Optional[str] = None

class PreProcessorOutput(BaseModel):
    student_id: UUID
    ts: datetime
    clean_text: str
    lang: Language
    emojis: List[str]
    toxicity: float
    emotion: Emotion
    intent: Intent
    topic_primary: Optional[Topic] = None
    topic_secondary: Optional[Topic] = None
    confidence: float
    rationale: Rationale
