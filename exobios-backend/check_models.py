import os
from google import genai
from dotenv import load_dotenv

# Load your API key
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("\n=== Your Allowed Models ===")
try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(f"Error checking models: {e}")