from openai import OpenAI
from openrouter_api_key import OPENROUTER_API_KEY

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def openrouter_llm(prompt: str, input_data: dict, model: str = "meta-llama/llama-3.3-70b-instruct:free") -> str:
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