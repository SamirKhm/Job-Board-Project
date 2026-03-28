from flask import Flask, request, jsonify
import os
import uuid
from resume_parser import extract_text
from llm_processor import extract_details
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def format_data(data):
    return {
        "name": data.get("name", ""),
        "skills": ", ".join(data.get("skills", [])),
        "education": data.get("education", ""),
        "experience": str(data.get("experience", "")),
        "summary": data.get("summary", "")
    }

@app.route("/")
def home():
    return "Server Running"


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    print("🔥 Request received")

    try:
        file = request.files["resume"]
        print("📄 File received:", file.filename)

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        print("✅ File saved")

        extracted_text = extract_text(filepath)
        print("📝 Text extracted length:", len(extracted_text))

        # extracted_text = extracted_text[:3000]
        extracted_text = extracted_text[:1500]
        print("🚀 Sending to LLM...")
        structured_data = extract_details(extracted_text)
        print("✅ LLM Done")
        print("🤖 LLM Output:", structured_data)
        formatted_data = format_data(structured_data)
        print("📦 Formatted Data:", formatted_data)

        return jsonify({
            "message": "Resume processed successfully",
            "data": structured_data
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)