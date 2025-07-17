import streamlit as st
from uuid import UUID
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from preprocessor import PreProcessorInput, PreProcessorOutput, override_intent_if_low_confidence, PREPROCESSOR_PROMPT
from profile_manager import ProfileManagerInput, ProfileManagerOutput, PROFILE_MANAGER_PROMPT
from summary_agent import SummaryAgentInput, postprocess_summary, SUMMARY_AGENT_PROMPT
from router import RouterInput, RouterOutput, ROUTER_PROMPT
from test_math_tutor_flow import call_agent  # Uses openrouter_llm now

st.set_page_config(page_title="Math Tutor Chat", page_icon="🧮")
st.title("🧮 Math Tutor Chat (OpenRouter-powered)")

def json_default(obj):
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=json_default)

def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception:
        return default

# Only keep the latest state, not a history
if "pre_out" not in st.session_state:
    st.session_state.pre_out = load_json("preprocessor.json", {})
if "prof_out" not in st.session_state:
    st.session_state.prof_out = load_json("profile_manager.json", {})
if "summary" not in st.session_state:
    st.session_state.summary = load_json("summary.json", {}).get("summary", "")

user_msg = st.chat_input("Type your math question or message...")

async def run_agents_async(user_msg, summary, profile):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        pre_input = PreProcessorInput(user_msg=user_msg, conversation_summary=summary)
        prof_input = ProfileManagerInput(user_msg=user_msg, updated_summary=summary, current_profile=profile)
        pre_future = loop.run_in_executor(executor, call_agent, PREPROCESSOR_PROMPT, pre_input.model_dump(), PreProcessorOutput)
        prof_future = loop.run_in_executor(executor, call_agent, PROFILE_MANAGER_PROMPT, prof_input.model_dump(), ProfileManagerOutput)
        pre_out, prof_out = await asyncio.gather(pre_future, prof_future)
    return pre_out, prof_out

if user_msg:
    # Run PreProcessor and Profile Manager in parallel
    pre_out, prof_out = asyncio.run(run_agents_async(user_msg, st.session_state.summary, st.session_state.prof_out))

    if isinstance(pre_out, PreProcessorOutput):
        pre_out = override_intent_if_low_confidence(pre_out)
        pre_out_dict = pre_out.model_dump()
        # Remove student_name and any student_id or UUID fields if present
        if "student_name" in pre_out_dict:
            del pre_out_dict["student_name"]
        if "student_id" in pre_out_dict:
            del pre_out_dict["student_id"]
        st.session_state.pre_out = pre_out_dict
    else:
        st.error("PreProcessor failed. Try again.")
        st.stop()

    if not isinstance(prof_out, ProfileManagerOutput):
        st.error("Profile Manager failed. Try again.")
        st.stop()

    # 3. Summary Agent (paragraph output)
    sum_input = SummaryAgentInput(
        user_msg=user_msg,
        preprocessor_output=st.session_state.pre_out,
        profile_delta=prof_out.model_dump(),
        prev_summary=st.session_state.summary
    )
    summary = call_agent(SUMMARY_AGENT_PROMPT, sum_input.model_dump())
    summary = postprocess_summary(summary)

    # 4. Router
    router_input = RouterInput(
        intent=pre_out.intent,
        confidence=pre_out.confidence,
        emotion=pre_out.emotion,
        profile_delta=prof_out.model_dump(),
        conversation_summary=summary
    )
    router_out = call_agent(ROUTER_PROMPT, router_input.model_dump(), RouterOutput)
    if not isinstance(router_out, RouterOutput):
        st.error("Router failed. Try again.")
        st.stop()

    # Update session state with only the latest data
    st.session_state.prof_out = prof_out.model_dump()
    st.session_state.summary = summary
    st.session_state.router_out = router_out.model_dump()

    # Overwrite JSON files with the latest data
    save_json(st.session_state.pre_out, "preprocessor.json")
    save_json(st.session_state.prof_out, "profile_manager.json")
    save_json({"summary": st.session_state.summary}, "summary.json")

# Display the latest state
st.subheader("PreProcessor Output (JSON)")
st.json(st.session_state.pre_out)

st.subheader("Profile Manager Output (JSON)")
st.json(st.session_state.prof_out)

st.subheader("Summary")
st.write(st.session_state.summary)

if "router_out" in st.session_state:
    st.subheader("Router Output (JSON)")
    st.json(st.session_state.router_out) 