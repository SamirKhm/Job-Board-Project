from groq import Groq
import json
import re
import os
from dotenv import load_dotenv

# 🔥 Load .env file
load_dotenv()

# 🔥 Get API key from env
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)
def extract_details(text):
    prompt = f"""
Extract the following details from the resume.

STRICT RULES:
- Return ONLY JSON
- No explanation
- No ```json
- No triple quotes
- Keep summary in one line

Format:
{{
  "name": "",
  "skills": [],
  "education": "",
  "experience": "",
  "summary": ""
}}

Resume:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )

        output = response.choices[0].message.content
        print("🔍 LLM Output:", output)

        # 🔥 FIX START
        output = re.sub(r"```json|```", "", output)

        match = re.search(r"\{.*\}", output, re.DOTALL)

        if match:
            json_text = match.group()
            json_text = json_text.replace('"""', '"')

            try:
                return json.loads(json_text)
            except Exception as e:
                print("❌ JSON Error:", e)
                return {"error": "Invalid JSON"}

        return {"error": "No JSON found"}
        # 🔥 FIX END

    except Exception as e:
        return {"error": str(e)}