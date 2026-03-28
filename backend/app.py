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


@app.route("/")
def home():
    return "Server Running"

@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    file = request.files["resume"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    extracted_text = extract_text(filepath)

    # 🔥 LLM processing
    structured_data = extract_details(extracted_text)

    return jsonify({
        "message": "Resume processed successfully",
        "data": structured_data
    })

if __name__ == "__main__":
    app.run(debug=True)