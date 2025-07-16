import google.generativeai as genai

genai.configure(api_key="AIzaSyBxE6V6khLW0WyiO04ib3zxyhVU9sSTH6I")

def gemini_llm(prompt: str, input_data: dict) -> str:
    # Format the input for Gemini: prompt + input as string
    full_prompt = prompt + "\n\nInput:\n" + str(input_data)
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(full_prompt)
    return response.text.strip()