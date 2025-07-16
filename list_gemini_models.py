import google.generativeai as genai

genai.configure(api_key="AIzaSyDRUlWPOWQFbKtmQ5FWm-LGx-C_Y3jO87k")

print("Available Gemini models:")
for m in genai.list_models():
    print(m.name) 