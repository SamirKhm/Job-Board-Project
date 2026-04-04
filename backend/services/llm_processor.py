import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"


# ------------------ JSON CLEANER ------------------
def fix_json(text):
    # Remove markdown
    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "").strip()

    # Extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    text = match.group(0)

    # Fix unquoted keys
    text = re.sub(r'([,{]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)

    # Replace single quotes with double quotes
    text = text.replace("'", '"')

    # Remove trailing commas
    text = re.sub(r",\s*([}\]])", r"\1", text)

    return text


# ------------------ EXPLANATION (LLM) ------------------
def generate_explanation(resume_skills, job_skills, score):
    prompt = f"""
Explain why the candidate is suitable or not suitable for the job.

Match Score: {score}%
Matching Skills: {resume_skills}
Job Skills: {job_skills}

IMPORTANT RULES:
- If matching skills list is empty, clearly say candidate is NOT a good match
- Do NOT add skills that are not in the matching list
- Keep answer short (1-2 lines)
- Be honest and logical
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        })
        print("🔍 LLM RAW RESPONSE:", response.json())

        return response.json().get("response", "").strip()

    except Exception as e:
        print("❌ LLM Explanation Error:", e)
        return "Explanation not available"


# ------------------ RESUME PARSER (LLM) ------------------
def extract_details(text):
    prompt = f"""
You are a JSON generator.

Extract details from the resume and return ONLY valid JSON.

STRICT RULES:
- Output ONLY JSON
- No explanation
- No extra text
- No markdown
- Keys MUST be in double quotes
- Strings MUST be in double quotes
- Skills must be a JSON array of strings

FORMAT:
{{
  "name": "string",
  "skills": ["skill1", "skill2"],
  "education": "string",
  "experience": "string",
  "summary": "string"
}}

Resume:
{text[:2000]}
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        })

        result = response.json()
        raw_output = result.get("response", "")

        print("🔍 RAW OUTPUT:", raw_output, flush=True)

        # -------- CLEAN JSON --------
        cleaned = fix_json(raw_output)

        if not cleaned:
            return fallback_response("No JSON found")

        try:
            parsed = json.loads(cleaned)
            return parsed

        except json.JSONDecodeError as e:
            print("❌ JSON ERROR:", e, flush=True)
            print("⚠️ Cleaned JSON:", cleaned, flush=True)
            return fallback_response("Invalid JSON after cleaning")

    except Exception as e:
        print("❌ LLM Error:", e)
        return fallback_response(str(e))


# ------------------ FALLBACK (IMPORTANT) ------------------
def fallback_response(reason=""):
    return {
        "name": "",
        "skills": [],
        "education": "",
        "experience": "",
        "summary": "",
        "warning": f"LLM parsing failed: {reason}"
    }