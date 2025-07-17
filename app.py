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
from persistent_memory_service import MemoryService
from ltm_agent import LTMConsolidationInput, consolidate_ltm, LTMProfile
from ltm_agent import STMTurn, STMPreprocessorOutput

st.set_page_config(page_title="Math Tutor Chat", page_icon="🧮")
st.title("🧮 Math Tutor Chat (OpenRouter-powered)")

# For demo: select student_id (could be from login/session in real app)
student_id = st.selectbox("Select Student", ["student-001", "student-002"])

# Initialize persistent memory service
memory_service = MemoryService("ltm_profiles.json", "backend_data.json")

def safe_pre_out(pre_out):
    # Defensive patch for topic_primary/secondary
    from preprocessor import PreProcessorOutput, override_intent_if_low_confidence
    import streamlit as st
    if isinstance(pre_out, PreProcessorOutput):
        pre_out_dict = pre_out.model_dump()
        for k in ["topic_primary", "topic_secondary"]:
            if k in pre_out_dict and (pre_out_dict[k] == "" or pre_out_dict[k] is None):
                pre_out_dict[k] = None
        pre_out = PreProcessorOutput(**pre_out_dict)
        pre_out = override_intent_if_low_confidence(pre_out)
        pre_out_dict = pre_out.model_dump()
        if "student_name" in pre_out_dict:
            del pre_out_dict["student_name"]
        if "student_id" in pre_out_dict:
            del pre_out_dict["student_id"]
        return pre_out, pre_out_dict
    else:
        st.error("PreProcessor failed. Try again.")
        st.stop()


# Function to reload and display the latest LTM profile from file
def display_ltm_profile(student_id):
    memory_service.ltm_data = memory_service._load_from_json(memory_service.ltm_filepath)
    profile = memory_service.get_student_profile(student_id)
    ltm_dict = profile.to_dict()
    with st.expander("Current Long-Term Memory (LTM) Profile", expanded=False):
        st.json(ltm_dict)
    return ltm_dict, profile

ltm_dict, profile = display_ltm_profile(student_id)

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
if "stm_turns" not in st.session_state:
    st.session_state.stm_turns = []

user_msg = st.chat_input("Type your math question or message...")

async def run_agents_async(user_msg, summary, profile, ltm_dict):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        pre_input = PreProcessorInput(user_msg=user_msg, conversation_summary=summary, ltm_profile=ltm_dict)
        prof_input = ProfileManagerInput(user_msg=user_msg, updated_summary=summary, current_profile=profile, ltm_profile=ltm_dict)
        pre_future = loop.run_in_executor(executor, call_agent, PREPROCESSOR_PROMPT, pre_input.model_dump(), PreProcessorOutput)
        prof_future = loop.run_in_executor(executor, call_agent, PROFILE_MANAGER_PROMPT, prof_input.model_dump(), ProfileManagerOutput)
        pre_out, prof_out = await asyncio.gather(pre_future, prof_future)
    return pre_out, prof_out

if user_msg:
    # Run PreProcessor and Profile Manager in parallel, passing LTM
    pre_out, prof_out = asyncio.run(run_agents_async(user_msg, st.session_state.summary, st.session_state.prof_out, ltm_dict))

    # Defensive patch for topic_primary/secondary
    pre_out, pre_out_dict = safe_pre_out(pre_out)
    st.session_state.pre_out = pre_out_dict

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

    # Save STM turn for LTM consolidation
    st.session_state.stm_turns.append({
        "user_msg": user_msg,
        "preprocessor_output": st.session_state.pre_out,
        "profile_manager_output": st.session_state.prof_out
    })

    # Overwrite JSON files with the latest data
    save_json(st.session_state.pre_out, "preprocessor.json")
    save_json(st.session_state.prof_out, "profile_manager.json")
    save_json({"summary": st.session_state.summary}, "summary.json")

    # --- AUTOMATIC LTM CONSOLIDATION ---
    ltm_dict, profile = display_ltm_profile(student_id)
    ltm_profile = student_profile_to_ltm_profile(profile)
    stm_turns = build_stm_turns(st.session_state.stm_turns[-5:])  # last 5 turns

    ltm_input = LTMConsolidationInput(
        student_id=student_id,
        current_ltm_profile=ltm_profile,
        short_term_memory=stm_turns
    )
    output = consolidate_ltm(ltm_input)
    updates = [op.model_dump() for op in output.updates]
    if updates:
        profile.apply_updates(updates)
        memory_service.save_student_profile(profile)
        st.success(f"LTM updated! Rationale: {output.rationale}")
        # Reload and display updated LTM
        ltm_dict, profile = display_ltm_profile(student_id)
    else:
        st.info("No significant LTM updates were proposed.")

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

def student_profile_to_ltm_profile(profile):
    # profile is a StudentProfile instance
    return LTMProfile(
        learning_style=profile.learning_style,
        motivation_type=getattr(profile, "motivation_type", None),
        goals=getattr(profile, "goals", []),
        mastered_topics=profile.mastered_topics,
        struggling_topics=profile.struggling_topics,
        emotion_baseline=getattr(profile, "emotion_baseline", None),
        performance_history=getattr(profile, "performance_history", {})
    )

def build_stm_turns(stm_turns_raw):
    stm_turns = []
    for i, turn in enumerate(stm_turns_raw):
        pre_out = turn.get("preprocessor_output", {})
        stm_pre_out = STMPreprocessorOutput(
            emotion=pre_out.get("emotion"),
            intent=pre_out.get("intent"),
            topic_primary=pre_out.get("topic_primary"),
            confidence=pre_out.get("confidence"),
        ) if pre_out else None
        stm_turns.append(
            STMTurn(
                turn=i+1,
                user_msg=turn.get("user_msg"),
                preprocessor_output=stm_pre_out,
                # Add more fields as needed
            )
        )
    return stm_turns 