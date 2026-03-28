from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()   # this will now read backend/.env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
def extract_details(text):
    prompt = f"""
    Extract the following details from the resume and return ONLY valid JSON:

    - name
    - skills (list)
    - experience
    - education
    - languages (list)

    Resume:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}  # 🔥 ensures valid JSON
        )

        result = response.choices[0].message.content.strip()
        return json.loads(result)

    except Exception as e:
        return {"error": str(e)}