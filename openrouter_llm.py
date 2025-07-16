from openai import OpenAI
from openrouter_api_key import API_KEY

def openrouter_llm(prompt: str, input_data: dict) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )
    full_prompt = prompt + "\n\nInput:\n" + str(input_data)
    completion = client.chat.completions.create(
        extra_headers={
            # Optionally set these for rankings:
            # "HTTP-Referer": "http://localhost:8501",  # or your deployed site
            # "X-Title": "Math Tutor Streamlit App",
        },
        model="openai/gpt-4o",
        messages=[
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=2048
    )
    content = completion.choices[0].message.content
    return content.strip() if content else "" 