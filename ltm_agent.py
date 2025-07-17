from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any, Union
from openrouter_llm import openrouter_llm

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

LTM_PROMPT = """You are a Cognitive Analysis Agent for an advanced AI math tutor. Your purpose is to act as the system's \"memory consolidation\" mechanism, similar to how a human brain processes experiences during sleep. You analyze a student's recent interactions (their Short-Term Memory) and decide what crucial information should be permanently stored in their Long-Term Memory (LTM).\n\nYour analysis must be conservative, evidence-based, and focused on identifying meaningful, persistent changes in the student's knowledge, emotional state, and learning preferences.\n\nInputs\nYou will be given the following JSON object as input:\n\n<see schema>\n\nCore Tasks\nAnalyze the short_term_memory: Read through the entire conversation history provided. Pay close attention to the student's words, the pre-processor's analysis (emotion, intent, topic), and any performance data.\n\nCompare with current_ltm_profile: Identify contradictions, confirmations, or new information. For example, if the student expresses fear about a topic already listed as struggling_topics, that confirms the profile. If they master a new topic, that's a significant update.\n\nSynthesize Key Insights: Based on your analysis, form high-level conclusions. Do not just repeat facts from the STM.\n\nPropose LTM Updates: Generate a JSON object containing specific, actionable changes for the LTM.\n\nInference Rules & Heuristics\nUse these rules to guide your decisions. You must find clear evidence in the short_term_memory for any proposed change.\n\nTopic Mastery & Struggle\nTo Master a Topic: The student must show strong evidence. A single correct answer is not enough. Look for a combination of:\n- High scores (> 0.9) on practice problems or quizzes.\n- Explicit statements like \"I get it now\" or \"This makes sense.\"\n- A shift in emotion from negative (fear, anger) to positive (joy, surprise) regarding the topic.\n\nTo Identify a Struggling Topic: Look for repeated patterns of:\n- Explicit statements like \"I'm lost,\" \"I don't understand.\"\n- Persistently negative emotions (fear, sadness, anger) across multiple turns on the same topic.\n- Low performance scores (< 0.5).\n- Asking for the same explanation multiple times.\n\nLearning Style & Preferences\nVisual: Did the student respond positively after being shown a diagram, graph, or visual example? (e.g., \"Oh, seeing it helps.\")\nTextual/Theoretical: Did the student ask for definitions, rules, or step-by-step text explanations?\nPractice-Oriented: Does the student frequently ask for practice problems (request_practice) after an explanation?\n\nEmotional Baseline & Trends\nIf a student consistently exhibits a specific emotion (e.g., anxiety) across multiple sessions or topics, consider updating the emotion_baseline.\nNote significant emotional shifts tied to specific events (e.g., from \"anxious\" to \"confident\" after mastering a topic).\n\nSemantic Memories (Core Moments)\nIdentify \"critical moments\" in the conversation that represent a significant turning point or a strong expression of the student's state. These are candidates for the Vector DB.\n\nGood candidates for semantic memories:\n- Strong emotional declarations: \"I finally understand this, thank you so much!\"\n- Clear statements of difficulty: \"This is the hardest part for me.\"\n- Statements of goals: \"I need to learn this for my exam next week.\"\n\nOutput Format\nRespond only with a valid JSON object in the following format. If no changes are warranted, return an empty updates array.\n\n{\n  \"student_id\": \"<copy from input>\",\n  \"rationale\": \"A brief, one-sentence summary of the key insight that led to these updates.\",\n  \"updates\": [ ... ]\n}\n\nDo not include any other text or commentary outside of the JSON response."""

def consolidate_ltm(stm_turns, ltm_profile):
    """
    stm_turns: list of dicts, each with 'agent' and 'output'
    ltm_profile: current LTM profile dict
    """
    # Construct prompt for LLM using all STM turns and current LTM
    # ... existing code ...
    response = openrouter_llm(LTM_PROMPT, input_obj.model_dump())
    # Parse the response as JSON and validate
    import json
    parsed = json.loads(response)
    return LTMConsolidationOutput(**parsed) 