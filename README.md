# Math Tutor Agent System

This repository contains production-grade prompt templates, type-safe schemas, and business logic for four core agents in an AI math tutor system:

## Agents

### 1. PreProcessor Agent
- **Purpose:** Classifies user messages (language, emotion, intent, topic, toxicity, confidence) and provides rationale.
- **Prompt:** See `preprocessor/prompt.py`
- **Schema:** See `preprocessor/schema.py`
- **Logic:** See `preprocessor/logic.py` (intent override for low confidence)

### 2. Profile Manager Agent
- **Purpose:** Tracks and evolves user-specific traits, knowledge, gaps, and behavior.
- **Prompt:** See `profile_manager/prompt.py`
- **Schema:** See `profile_manager/schema.py`
- **Logic:** See `profile_manager/logic.py` (profile delta computation)

### 3. Router Agent
- **Purpose:** Routes the message to the appropriate processing module based on intent, confidence, emotion, and profile gaps.
- **Prompt:** See `router/prompt.py`
- **Schema:** See `router/schema.py`
- **Logic:** See `router/logic.py` (routing rules)

### 4. Summary Agent
- **Purpose:** Summarizes the conversation so far, incorporating the latest message, PreProcessor output, and Profile Manager delta. The summary is used as input for the PreProcessor and Profile Manager in future turns.
- **Prompt:** See `summary_agent/prompt.py`
- **Schema:** See `summary_agent/schema.py`
- **Logic:** See `summary_agent/logic.py` (optional post-processing)

## Usage
- Import the relevant agent module and use the prompt, schema, and logic as needed.
- Prompts are ready for injection into LangChain or LangGraph LLM chains.
- All schemas are type-safe using Pydantic.

## Requirements
```
pip install -r requirements.txt
```

## Extending
- Add more agents or extend logic as needed for your math tutor system. 