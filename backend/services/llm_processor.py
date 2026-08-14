import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"


# ============================================================
# JSON CLEANER
# ============================================================

def fix_json(text):

    # Remove markdown
    text = re.sub(
        r"```[a-zA-Z]*",
        "",
        text
    )

    text = text.replace(
        "```",
        ""
    ).strip()


    # Extract JSON block
    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        return None


    text = match.group(0)


    # Fix unquoted keys
    text = re.sub(
        r'([,{]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:',
        r'\1"\2":',
        text
    )


    # Replace single quotes with double quotes
    text = text.replace(
        "'",
        '"'
    )


    # Remove trailing commas
    text = re.sub(
        r",\s*([}\]])",
        r"\1",
        text
    )


    return text


# ============================================================
# EXPLANATION (LLM)
# ============================================================

def generate_explanation(
    matched_skills,
    missing_skills,
    match_score,
    semantic_score,
    skill_score,
    experience_score,
    education_score
):

    prompt = f"""
Explain this candidate-job match in 1-2 short sentences.

AMSM Match Score: {match_score}%

Semantic Score: {semantic_score}%
Skill Score: {skill_score}%
Experience Score: {experience_score}%
Education Score: {education_score}%

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Rules:
- Do not invent skills.
- Mention missing skills if present.
- Mention education mismatch if education score is 0.
- Mention experience mismatch if experience score is below 100.
- Keep it concise.
"""


    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0
                }
            }
        )


        response.raise_for_status()


        result = response.json()


        explanation = result.get(
            "response",
            ""
        ).strip()


        if explanation:

            return explanation


        return (
            "Candidate matches the required "
            "skills and job criteria."
        )


    except Exception as e:

        print(
            "❌ LLM Explanation Error:",
            e
        )


        # ----------------------------------------------------
        # FALLBACK EXPLANATION
        # ----------------------------------------------------

        if missing_skills:

            return (
                f"The candidate matches "
                f"{len(matched_skills)} required skills, "
                f"but is missing: "
                f"{', '.join(missing_skills)}."
            )


        elif education_score < 100:

            return (
                "The candidate matches the required skills, "
                "but the required education qualification "
                "is not fully satisfied."
            )


        elif experience_score < 100:

            return (
                "The candidate matches the required skills, "
                "but does not fully satisfy the required "
                "experience."
            )


        else:

            return (
                "The candidate matches all required skills "
                "and satisfies the evaluated job criteria."
            )


# ============================================================
# RESUME PARSER (LLM)
# ============================================================

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

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0
                }
            }
        )


        result = response.json()


        raw_output = result.get(
            "response",
            ""
        )


        print(
            "🔍 RAW OUTPUT:",
            raw_output,
            flush=True
        )


        # ----------------------------------------------------
        # CLEAN JSON
        # ----------------------------------------------------

        cleaned = fix_json(
            raw_output
        )


        if not cleaned:

            return fallback_response(
                "No JSON found"
            )


        try:

            parsed = json.loads(
                cleaned
            )

            return parsed


        except json.JSONDecodeError as e:

            print(
                "❌ JSON ERROR:",
                e,
                flush=True
            )


            print(
                "⚠️ Cleaned JSON:",
                cleaned,
                flush=True
            )


            return fallback_response(
                "Invalid JSON after cleaning"
            )


    except Exception as e:

        print(
            "❌ LLM Error:",
            e
        )


        return fallback_response(
            str(e)
        )


# ============================================================
# FALLBACK
# ============================================================

def fallback_response(
    reason=""
):

    return {

        "name": "",

        "skills": [],

        "education": "",

        "experience": "",

        "summary": "",

        "warning":
            f"LLM parsing failed: {reason}"
    }