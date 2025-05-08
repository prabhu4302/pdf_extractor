import os
from flask import Flask, render_template, request, redirect, flash
import fitz  # PyMuPDF
import re
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your-secret-key-here'

# Expected course titles (can be expanded)
EXPECTED_COURSES = {
    "Living up to Our Commitments RCM Training": "RCM Training",
    "Don't Feed The 'ish": "DFT Training",
    "Working In Partnership with BT": "BT Partnership"
}

def validate_certificate(text, filename):
    """Verify if the certificate matches expected patterns"""
    errors = []
    
    # Check all required fields exist
    if "This is to certify that" not in text:
        errors.append("Missing certification statement")
    if "has completed" not in text:
        errors.append("Missing completion statement")
    if "on" not in text and "completed by" not in text:
        errors.append("Missing completion date")
    
    # Check for suspicious patterns
    if "Certificate of Completion" not in text:
        errors.append("Missing certificate header")
    
    return errors if errors else None

def extract_fields_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    # Validate certificate first
    validation_errors = validate_certificate(text, os.path.basename(pdf_path))
    if validation_errors:
        return {
            "Filename": os.path.basename(pdf_path),
            "Status": "Invalid",
            "Errors": validation_errors,
            "Raw Text": text.strip()
        }

    # Extract fields with more robust patterns
    name_match = re.search(r"This is to certify that\s+(.*?)\s+has (?:successfully )?completed", text, re.DOTALL)
    course_match = re.search(r"completed\s+(.*?)\s+(?:on|with a score of|$)", text, re.DOTALL)
    date_match = re.search(r"(?:on|completed by)\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)

    # Standardize course title if it matches expected courses
    course_title = course_match.group(1).strip() if course_match else "Not found"
    standardized_title = EXPECTED_COURSES.get(course_title, course_title)

    return {
        "Filename": os.path.basename(pdf_path),
        "Name": name_match.group(1).strip() if name_match else "Not found",
        "Course Title": standardized_title,
        "Completion Date": date_match.group(1).strip() if date_match else "Not found",
        "Status": "Valid",
        "Raw Text": text.strip()
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_data = []
    if request.method == 'POST':
        files = [
            request.files.get('pdf_file_1'),
            request.files.get('pdf_file_2'),
            request.files.get('pdf_file_3')
        ]

        valid_files = [file for file in files if file and file.filename != '']

        if not valid_files:
            flash('Please upload at least one PDF file')
            return redirect(request.url)

        for file in valid_files:
            if not file.filename.lower().endswith('.pdf'):
                flash(f'File {file.filename} is not a PDF')
                continue

            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                extracted = extract_fields_from_pdf(file_path)
                extracted_data.append(extracted)
                
                if extracted.get('Status') == 'Invalid':
                    flash(f'Invalid certificate detected in {file.filename}')
            except Exception as e:
                flash(f'Error processing {file.filename}: {str(e)}')

    return render_template('index.html', extracted=extracted_data)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
