# Math Tutor Streamlit App

This is a production-ready, multi-turn math tutor chat app powered by OpenRouter (via the OpenAI SDK) and Streamlit.

## Features
- Real-time math tutor chat with PreProcessor, Profile Manager, Summary Agent, and Router agents
- Uses OpenRouter (via `openai` Python SDK) for LLM-powered classification and routing
- Clean, modern Streamlit UI
- Only the latest PreProcessor, Profile Manager, and summary JSONs are saved and displayed
- No user name or UUIDs in the output
- **Long-Term Memory (LTM) Consolidation Agent** for evidence-based, type-safe student profile updates

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run app.py
```
Open the provided local URL in your browser to chat with the math tutor.

## Configuration
- Set your OpenRouter API key in `openrouter_api_key.py`.
- The default LLM is `meta-llama/llama-3.3-70b-instruct:free` (changeable in `openrouter_llm.py`).

## Project Structure
- `app.py` — Main Streamlit app
- `preprocessor/`, `profile_manager/`, `summary_agent/`, `router/` — Agent logic and schemas
- `ltm_agent.py` — LTM Consolidation Agent classes and logic
- `openrouter_llm.py` — OpenRouter LLM utility
- `openrouter_api_key.py` — API key (do not share this file)
- `requirements.txt` — Python dependencies

---

## Long-Term Memory (LTM) Consolidation Agent

### **Purpose**
- Analyzes a student's recent short-term memory (STM) and current LTM profile.
- Proposes evidence-based, high-level updates to the student's long-term profile.
- Returns a JSON object with rationale and actionable updates.

### **Key Classes**
- `LTMProfile`: Student's long-term profile (learning style, goals, topics, etc.)
- `STMTurn`: One turn in short-term memory (user/bot message, preprocessor output, etc.)
- `LTMConsolidationInput`: Input object for the agent
- `LTMUpdateOperation` / `LTMConsolidationOutput`: Output schema for LTM updates

### **How to Use**

```python
from ltm_agent import (
    LTMProfile, STMTurn, STMPreprocessorOutput, LTMConsolidationInput, consolidate_ltm
)

ltm_profile = LTMProfile(
    learning_style="visual",
    motivation_type=None,
    goals=["pass_final_exam"],
    mastered_topics=["algebra_linear"],
    struggling_topics=[],
    emotion_baseline="anxious",
    performance_history={"algebra_quiz_1": 0.85}
)

stm = [
    STMTurn(
        turn=1,
        user_msg="I hate trigonometry, I'm never going to get it.",
        preprocessor_output=STMPreprocessorOutput(emotion="anger", topic_primary="trigonometry_basic", confidence=0.6)
    ),
    # ... more turns ...
]

input_obj = LTMConsolidationInput(
    student_id="a1b2-c3d4-e5f6",
    current_ltm_profile=ltm_profile,
    short_term_memory=stm
)

output = consolidate_ltm(input_obj)
print(output.model_dump_json(indent=2))
```

### **Prompt and Inference Rules**
- The LTM agent uses a detailed prompt (see `ltm_agent.py`) to ensure only evidence-based, meaningful changes are proposed.
- The output is always a valid JSON object with a rationale and a list of update operations.

---

## OpenRouter LLM Utility
- All LLM calls use the OpenAI Python SDK with OpenRouter as the backend.
- The utility in `openrouter_llm.py` can be used for any prompt/input, not just LTM.

**Example:**
```python
from openrouter_llm import openrouter_llm
response = openrouter_llm("Summarize this:", {"text": "Math is fun!"})
print(response)
```

---
**For any further customization or questions, see the code or ask for help!** 