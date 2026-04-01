import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def extract_details(text):
    prompt = f"""
Extract the following details from the resume.

STRICT RULES:
- Return ONLY JSON
- No explanation

Format:
{{
  "name": "",
  "skills": [],
  "education": "",
  "experience": "",
  "summary": ""
}}

Resume:
{text[:2000]}
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        })

        result = response.json()
        output = result.get("response", "")

        print("🔍 Ollama Output:", output)

        # Clean output
        output = re.sub(r"```json|```", "", output)

        match = re.search(r"\{.*\}", output, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except:
                return {"error": "Invalid JSON"}

        return {"error": "No JSON found"}

    except Exception as e:
        return {"error": str(e)}