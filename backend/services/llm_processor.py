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
    required_skills,
    matched_skills,
    missing_skills,
    skill_gap_percentage,
    match_score,
    semantic_score,
    skill_score,
    experience_score,
    education_score
):

    # --------------------------------------------------------
    # BASIC COUNTS
    # --------------------------------------------------------

    total_required = len(required_skills)
    total_matched = len(matched_skills)
    total_missing = len(missing_skills)

    # --------------------------------------------------------
    # EXPERIENCE STATUS
    # --------------------------------------------------------

    if experience_score >= 100:

        experience_status = (
            "The stated experience requirement is satisfied."
        )

    elif experience_score <= 0:

        experience_status = (
            "The evaluated experience requirement is not satisfied."
        )

    else:

        experience_status = (
            "The stated experience requirement is partially satisfied."
        )

    # --------------------------------------------------------
    # EDUCATION STATUS
    # --------------------------------------------------------

    if education_score >= 100:

        education_status = (
            "The education requirement is satisfied."
        )

    else:

        education_status = (
            "There is an education mismatch."
        )

    # --------------------------------------------------------
    # SKILL STATUS
    # --------------------------------------------------------

    if total_missing == 0:

        skill_status = (
            f"The candidate matches all {total_required} "
            f"required skills, resulting in a 0% skill gap."
        )

    else:

        skill_status = (
            f"The candidate matches {total_matched} of "
            f"{total_required} required skills and is missing "
            f"{total_missing} skills, resulting in a "
            f"{skill_gap_percentage:.2f}% skill gap."
        )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
Explain why the candidate received an AMSM match score of
{match_score:.2f}%.

Write exactly 2-3 concise sentences.

AMSM COMPONENTS:

AMSM Match Score: {match_score:.2f}%
Semantic Score: {semantic_score:.2f}%
Skill Score: {skill_score:.2f}%
Experience Score: {experience_score:.2f}%
Education Score: {education_score:.2f}%

SKILL ANALYSIS:

Required Skills ({total_required}):
{required_skills}

Matched Skills ({total_matched}):
{matched_skills}

Missing Skills ({total_missing}):
{missing_skills}

Skill Gap:
{skill_gap_percentage:.2f}%

VERIFIED SKILL STATUS:
{skill_status}

VERIFIED EXPERIENCE STATUS:
{experience_status}

VERIFIED EDUCATION STATUS:
{education_status}

RULES:

1. Explain the reason for the AMSM score using ONLY the information provided.

2. Connect the final AMSM score with the component scores.

3. Explain the effect of the skill coverage and skill gap on the score.

4. If the skill gap is 0%, explicitly state that all required skills are matched.

5. If the skill gap is greater than 0%, explicitly state how many required skills are missing.

6. Mention the matched and missing skills when useful.

7. Use the exact provided skill gap percentage.

8. Do not calculate or invent another skill gap.

9. Do not invent skills, qualifications, or experience.

10. Never say that a matched skill is missing.

11. Never say that a missing skill is matched.

12. If Education Score is 100%, explicitly state that the education requirement is satisfied.

13. If Education Score is below 100%, mention the education mismatch.

14. If Experience Score is 100%, state only that the stated experience requirement is satisfied.

15. Do NOT claim that the candidate has professional work experience unless explicitly provided.

16. Projects are not professional employment.

17. Do not use phrases such as "strong skill match" when significant skills are missing.

18. Do not call the candidate a "strong match" based on the semantic score alone.

19. Mention the Semantic Score as one factor contributing to the final AMSM score.

20. Do not explain the AMSM mathematical formula.

21. Do not make claims that cannot be derived from the supplied information.

22. Keep the explanation factual and concise.
"""

    # --------------------------------------------------------
    # CALL OLLAMA
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # EMPTY RESPONSE → FALLBACK
        # ----------------------------------------------------

        return generate_fallback_explanation(
            required_skills,
            matched_skills,
            missing_skills,
            skill_gap_percentage,
            match_score,
            semantic_score,
            skill_score,
            experience_score,
            education_score
        )

    except Exception as e:

        print(
            "❌ LLM Explanation Error:",
            e
        )

        return generate_fallback_explanation(
            required_skills,
            matched_skills,
            missing_skills,
            skill_gap_percentage,
            match_score,
            semantic_score,
            skill_score,
            experience_score,
            education_score
        )
        
# ============================================================
# FALLBACK EXPLANATION
# ============================================================

def generate_fallback_explanation(
    required_skills,
    matched_skills,
    missing_skills,
    skill_gap_percentage,
    match_score,
    semantic_score,
    skill_score,
    experience_score,
    education_score
):

    total_required = len(required_skills)
    total_matched = len(matched_skills)
    total_missing = len(missing_skills)

    # --------------------------------------------------------
    # SKILL PART
    # --------------------------------------------------------

    if total_missing == 0:

        skill_part = (
            f"The candidate matches all {total_required} "
            f"required skills, resulting in a 0% skill gap."
        )

    else:

        skill_part = (
            f"The candidate matches {total_matched} of "
            f"{total_required} required skills, with "
            f"{total_missing} skills missing and a "
            f"{skill_gap_percentage:.2f}% skill gap."
        )

    # --------------------------------------------------------
    # EXPERIENCE PART
    # --------------------------------------------------------

    if experience_score >= 100:

        experience_part = (
            "The stated experience requirement is satisfied."
        )

    elif experience_score <= 0:

        experience_part = (
            "The evaluated experience requirement is not satisfied."
        )

    else:

        experience_part = (
            "The stated experience requirement is partially satisfied."
        )

    # --------------------------------------------------------
    # EDUCATION PART
    # --------------------------------------------------------

    if education_score >= 100:

        education_part = (
            "The education requirement is satisfied."
        )

    else:

        education_part = (
            "There is an education mismatch."
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    return (
        f"The AMSM match score is {match_score:.2f}%, "
        f"with a semantic score of {semantic_score:.2f}% "
        f"and a skill score of {skill_score:.2f}%. "
        f"{skill_part} "
        f"{experience_part} "
        f"{education_part}"
    )
# ============================================================
# RESUME PARSER (LLM)
# ============================================================

def extract_details(text):

    prompt = f"""
Extract information from the resume.

Return ONLY a valid JSON object.

IMPORTANT RULES:
1. Do NOT add markdown.
2. Do NOT add comments.
3. Do NOT add explanations.
4. Do NOT invent information.
5. Only extract skills explicitly present in the resume.
6. Do not infer skills that are not explicitly stated.
7. "skills" MUST be an array of strings.
8. "education" MUST contain the actual education information if present.
9. "experience" MUST contain actual employment experience if present.
10. Projects can be included in experience only if clearly described as project experience.
11. Every JSON key and string MUST use double quotes.
12. The output MUST be valid JSON.

Use exactly this structure:

{{
  "name": "",
  "skills": [],
  "education": "",
  "experience": "",
  "summary": ""
}}

Resume:

{text[:6000]}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "format": "json",
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

        cleaned = fix_json(raw_output)

        if not cleaned:
            print("❌ No JSON found", flush=True)
            return fallback_response("No JSON found")

        try:

            parsed = json.loads(cleaned)

            skills = parsed.get("skills", [])

            if not isinstance(skills, list):
                skills = []

            parsed["skills"] = skills

            print(
                "✅ PARSED SKILLS:",
                skills,
                flush=True
            )

            print(
                "🎓 EDUCATION:",
                parsed.get("education", ""),
                flush=True
            )

            print(
                "💼 EXPERIENCE:",
                parsed.get("experience", ""),
                flush=True
            )

            return parsed

        except json.JSONDecodeError as e:

            print("❌ JSON ERROR:", e, flush=True)
            print("⚠️ Cleaned JSON:", cleaned, flush=True)

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