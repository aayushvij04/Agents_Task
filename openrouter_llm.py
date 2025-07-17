from openai import OpenAI
from openrouter_api_key import OPENROUTER_API_KEY

if not OPENROUTER_API_KEY or not isinstance(OPENROUTER_API_KEY, str):
    raise RuntimeError("OpenRouter API key is missing or not a string. Please check openrouter_api_key.py.")

print(f"[OpenRouter LLM] Using API key: {OPENROUTER_API_KEY[:8]}...{'*' * (len(OPENROUTER_API_KEY)-12)}{OPENROUTER_API_KEY[-4:]}")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def openrouter_llm(prompt: str, input_data: dict, model: str = "openai/gpt-3.5-turbo") -> str:
    user_message = f"{prompt}\n\nInput:\n{input_data}"
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": user_message}
        ],
        extra_headers={
            # Optionally set these for OpenRouter ranking
            # "HTTP-Referer": "<YOUR_SITE_URL>",
            # "X-Title": "Math Tutor Streamlit App",
        },
        extra_body={},
    )
    return completion.choices[0].message.content.strip()

if __name__ == "__main__":
    print("\n[OpenRouter LLM] Running minimal test...")
    try:
        result = openrouter_llm("Say hello to the world.", {})
        print("[OpenRouter LLM] Test result:", result)
    except Exception as e:
        print("[OpenRouter LLM] Test failed:", e) 