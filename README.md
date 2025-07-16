# Math Tutor Streamlit App

This is a production-ready, multi-turn math tutor chat app powered by Google Gemini and Streamlit.

## Features
- Real-time math tutor chat with PreProcessor, Profile Manager, Summary Agent, and Router agents
- Uses Google Gemini (via `google-generativeai`) for LLM-powered classification and routing
- Clean, modern Streamlit UI
- Only the latest PreProcessor, Profile Manager, and summary JSONs are saved and displayed
- No user name or UUIDs in the output

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
- Set your Gemini API key in `gemini_api_key.py`.

## Project Structure
- `app.py` — Main Streamlit app
- `preprocessor/`, `profile_manager/`, `summary_agent/`, `router/` — Agent logic and schemas
- `gemini_llm.py` — Gemini LLM utility
- `gemini_api_key.py` — API key (do not share this file)
- `requirements.txt` — Python dependencies

---
**For any further customization or questions, see the code or ask for help!** 