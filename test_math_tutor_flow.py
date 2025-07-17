from preprocessor import PreProcessorInput, PreProcessorOutput, override_intent_if_low_confidence, PREPROCESSOR_PROMPT
from profile_manager import ProfileManagerInput, ProfileManagerOutput, compute_profile_delta, PROFILE_MANAGER_PROMPT
from summary_agent import SummaryAgentInput, SummaryAgentOutput, postprocess_summary, SUMMARY_AGENT_PROMPT
from router import RouterInput, RouterOutput, route_message, ROUTER_PROMPT
from uuid import uuid4, UUID
from datetime import datetime
from openrouter_llm import openrouter_llm
import json
import sys

# Utility to call OpenRouter and parse JSON output
def call_agent(prompt, input_data, output_model=None):
    response_text = openrouter_llm(prompt, input_data)
    if output_model:
        try:
            # Find the first { ... } block in the response
            json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
            import json
            data = json.loads(json_str)
            # Patch: convert empty topic strings to None
            for k in ["topic_primary", "topic_secondary"]:
                if k in data and (data[k] == "" or data[k] is None):
                    data[k] = None
            # Patch student_id if needed (legacy, not used now)
            if output_model.__name__ == "PreProcessorOutput" and 'replace_with_uuid' in json_str:
                import re
                data['student_id'] = str(uuid4())
            return output_model(**data)
        except Exception as e:
            print("Error parsing OpenRouter output:", e)
            print("Raw output:", response_text)
            return response_text
    return response_text

def ensure_model(obj, model_type, label):
    if not isinstance(obj, model_type):
        print(f"\n[ERROR] {label} did not return a valid {model_type.__name__}. Raw output:")
        print(obj)
        sys.exit(1)

def main():
    user_msg = "Can you explain how to solve x + 2 = 7?"
    prev_summary = ""
    current_profile = {}

    # 1. PreProcessor
    pre_input = PreProcessorInput(user_msg=user_msg, conversation_summary=prev_summary)
    pre_out = call_agent(PREPROCESSOR_PROMPT, pre_input.model_dump(), PreProcessorOutput)
    ensure_model(pre_out, PreProcessorOutput, "PreProcessor")
    if isinstance(pre_out, PreProcessorOutput):
        pre_out = override_intent_if_low_confidence(pre_out)
        print("\n[PreProcessor Output]\n", pre_out.model_dump_json(indent=2))
    else:
        print("\n[ERROR] PreProcessor (after call_agent) did not return a valid PreProcessorOutput. Raw output:")
        print(pre_out)
        sys.exit(1)
    if not isinstance(pre_out, PreProcessorOutput):
        print("\n[ERROR] PreProcessor (after override) did not return a valid PreProcessorOutput. Raw output:")
        print(pre_out)
        sys.exit(1)

    # 2. Profile Manager
    prof_input = ProfileManagerInput(user_msg=user_msg, updated_summary=prev_summary, current_profile=current_profile)
    prof_out = call_agent(PROFILE_MANAGER_PROMPT, prof_input.model_dump(), ProfileManagerOutput)
    ensure_model(prof_out, ProfileManagerOutput, "Profile Manager")
    print("\n[Profile Manager Output]\n", prof_out.model_dump_json(indent=2))

    # 3. Summary Agent
    sum_input = SummaryAgentInput(
        user_msg=user_msg,
        preprocessor_output=pre_out.model_dump(),
        profile_delta=prof_out.model_dump(),
        prev_summary=prev_summary
    )
    sum_out = call_agent(SUMMARY_AGENT_PROMPT, sum_input.model_dump(), SummaryAgentOutput)
    ensure_model(sum_out, SummaryAgentOutput, "Summary Agent")
    if not isinstance(sum_out, SummaryAgentOutput):
        print("\n[ERROR] Summary Agent did not return a valid SummaryAgentOutput. Raw output:")
        print(sum_out)
        sys.exit(1)
    summary = postprocess_summary(sum_out.summary)
    print("\n[Summary Agent Output]\n", summary)

    # 4. Router
    router_input = RouterInput(
        intent=pre_out.intent,
        confidence=pre_out.confidence,
        emotion=pre_out.emotion,
        profile_delta=prof_out.model_dump(),
        conversation_summary=summary
    )
    router_out = call_agent(ROUTER_PROMPT, router_input.model_dump(), RouterOutput)
    ensure_model(router_out, RouterOutput, "Router")
    if not isinstance(router_out, RouterOutput):
        print("\n[ERROR] Router did not return a valid RouterOutput. Raw output:")
        print(router_out)
        sys.exit(1)
    print("\n[Router Output]\n", router_out.model_dump_json(indent=2))

if __name__ == "__main__":
    main() 