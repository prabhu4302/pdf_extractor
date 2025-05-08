import os
from flask import Flask, render_template, request, redirect
import fitz  # PyMuPDF
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def extract_fields_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    name_match = re.search(r"This is to certify that\s+(.*?)\s+has completed", text, re.DOTALL)
    course_match = re.search(r"has completed\s+(.*?)\s+on", text, re.DOTALL)
    date_match = re.search(r"on\s+([^\n]+)", text)

    return {
        "Filename": os.path.basename(pdf_path),
        "Name": name_match.group(1).strip() if name_match else "Not found",
        "Course Title": course_match.group(1).strip() if course_match else "Not found",
        "Completion Date": date_match.group(1).strip() if date_match else "Not found",
        "Raw Text": text.strip()
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_data = []
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')

        if not files or len(files) == 0:
            return redirect(request.url)

        for file in files[:3]:  # limit to 3 files
            if file and file.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                extracted = extract_fields_from_pdf(file_path)
                extracted_data.append(extracted)

    return render_template('index.html', extracted=extracted_data)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
