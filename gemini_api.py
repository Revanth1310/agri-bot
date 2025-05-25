import requests
import json

GEMINI_API_KEY = "AIzaSyDFpGI9l0LlM2EZgiv6NwVjQlZuuVLcuk0"

def query_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    full_url = f"{url}?key={GEMINI_API_KEY}"
    response = requests.post(full_url, headers=headers, json=payload)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "❌ Error fetching Gemini response. Check API key or prompt formatting."
