import PyPDF2
import docx
import os

# 🔹 Extract text from PDF
def extract_text_from_pdf(filepath):
    text = ""
    try:
        with open(filepath, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("Error reading PDF:", e)
    return text


# 🔹 Extract text from DOCX
def extract_text_from_docx(filepath):
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print("Error reading DOCX:", e)
    return text


# 🔹 Main function (used in app.py)
def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(filepath)

    elif ext == ".docx":
        return extract_text_from_docx(filepath)

    else:
        return "Unsupported file format"