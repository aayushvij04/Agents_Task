from .schema import LTMConsolidationInput, LTMProfile
from .prompt import LTM_PROMPT
from openrouter_llm import openrouter_llm

import json

def consolidate_ltm(stm_turns, ltm_profile):
    """
    stm_turns: list of STMTurn objects
    ltm_profile: LTMProfile object
    """
    # Create the input object for the LLM
    input_obj = LTMConsolidationInput(
        student_id=getattr(ltm_profile, "student_id", "unknown"),
        current_ltm_profile=ltm_profile,
        short_term_memory=stm_turns
    )
    response = openrouter_llm(LTM_PROMPT, input_obj.model_dump())
    # Parse the response as JSON and validate
    parsed = json.loads(response)
    return LTMProfile(**parsed) 