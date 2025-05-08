import os
from flask import Flask, render_template, request, redirect, flash
import fitz  # PyMuPDF
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your-secret-key-here'  # Required for flashing messages

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
        # Get all three possible file inputs
        files = [
            request.files.get('pdf_file_1'),
            request.files.get('pdf_file_2'),
            request.files.get('pdf_file_3')
        ]

        # Filter out empty file inputs
        valid_files = [file for file in files if file and file.filename != '']

        if not valid_files:
            flash('Please upload at least one PDF file')
            return redirect(request.url)

        for file in valid_files:
            if file.filename.endswith('.pdf'):
                try:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(file_path)
                    extracted = extract_fields_from_pdf(file_path)
                    extracted_data.append(extracted)
                except Exception as e:
                    flash(f'Error processing {file.filename}: {str(e)}')
            else:
                flash(f'File {file.filename} is not a PDF')

    return render_template('index.html', extracted=extracted_data)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
