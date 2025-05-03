import os
from flask import Flask, render_template, request, redirect, url_for
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
        "Name": name_match.group(1).strip() if name_match else "Not found",
        "Course Title": course_match.group(1).strip() if course_match else "Not found",
        "Completion Date": date_match.group(1).strip() if date_match else "Not found",
        "Raw Text": text.strip()
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return redirect(request.url)

        file = request.files['pdf_file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            extracted = extract_fields_from_pdf(file_path)
            return render_template('index.html', extracted=extracted)

    return render_template('index.html', extracted=None)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
