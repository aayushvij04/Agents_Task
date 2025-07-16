from .schema import RouterInput, RouterOutput, WorkerRoute
from typing import Any

def route_message(input: RouterInput) -> RouterOutput:
    # 1. If confidence < 0.55 → always route to "support"
    if input.confidence < 0.55:
        return RouterOutput(route="support", reason="Confidence is low (<0.55), student may need support.")
    # 2. If intent == "greeting" or "chit_chat" AND there are profile gaps → route to "profile_gap"
    if input.intent in ("greeting", "chit_chat") and input.profile_delta.get("profile_gaps"):
        return RouterOutput(route="profile_gap", reason="Idle/small-talk and profile has missing fields.")
    # 3. If intent is uncertain OR no topic detected → route to "clarifier"
    if input.intent == "uncertain" or not input.profile_delta.get("new_facts", {}).get("recent_topic"):
        return RouterOutput(route="clarifier", reason="Intent is uncertain or no topic detected.")
    # 4. If intent matches an explain/practice/support type → route accordingly
    if input.intent == "ask_explanation":
        return RouterOutput(route="explain", reason="User wants a step-by-step explanation.")
    if input.intent == "request_practice":
        return RouterOutput(route="practice", reason="User requests problems or exercises.")
    if input.intent in ("emotional_support", "request_motivation"):
        return RouterOutput(route="support", reason="User wants encouragement or emotional support.")
    # Default fallback
    return RouterOutput(route="clarifier", reason="Default fallback: intent/topic not clearly mapped.")
