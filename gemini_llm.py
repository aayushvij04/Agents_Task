import google.generativeai as genai
from gemini_api_key import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def gemini_llm(prompt: str, input_data: dict) -> str:
    # Format the input for Gemini: prompt + input as string
    full_prompt = prompt + "\n\nInput:\n" + str(input_data)
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(full_prompt)
    return response.text.strip()