import os
from flask import Flask, render_template, request, redirect, flash
import fitz  # PyMuPDF
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your-secret-key-here'

# Approved course patterns
APPROVED_COURSES = {
    r"(?i)living up to our commitments rcm training": "RCM",
    r"(?i)working in partnership with bt": "BT-PART",
    r"(?i)[^\w]*don't[^\w]*feed[^\w]*the[^\w]*'ish": "DFT"
}

def extract_certificate_data(text):
    """Attempt to extract name, course, and date from PDF text"""
    patterns = [
        {
            'name': re.compile(r"certificate of completion.*?This is to certify that\s*(.*?)\s*has completed", re.DOTALL | re.IGNORECASE),
            'course': re.compile(r"has completed\s*(.*?)\s*on", re.DOTALL | re.IGNORECASE),
            'date': re.compile(r"on\s*(\d{1,2}/\d{1,2}/\d{4})")
        },
        {
            'name': re.compile(r"certificate.*?awarded to\s*(.*?)\s*for", re.DOTALL | re.IGNORECASE),
            'course': re.compile(r"for\s*(.*?)\s*completed", re.DOTALL | re.IGNORECASE),
            'date': re.compile(r"completed on\s*(\d{1,2}/\d{1,2}/\d{4})")
        }
    ]

    for pattern in patterns:
        try:
            name_match = pattern['name'].search(text)
            course_match = pattern['course'].search(text)
            date_match = pattern['date'].search(text)
            if name_match and course_match:
                return {
                    'name': name_match.group(1).strip(),
                    'course': course_match.group(1).strip(),
                    'date': date_match.group(1) if date_match else "Date not found"
                }
        except Exception:
            continue

    return None

def verify_certificate(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        print(f"=== Extracted from {pdf_path} ===")
        print(text)
        print("=== END ===")

        data = extract_certificate_data(text)
        if not data:
            print(f"❌ Could not extract structured data from: {pdf_path}")
            return None

        course_title = data['course']
        course_code = None

        for pattern, code in APPROVED_COURSES.items():
            if re.search(pattern, course_title, re.IGNORECASE):
                course_code = code
                break

        if not course_code:
            print(f"❌ Course not approved: {course_title}")
            return None

        return {
            "name": data['name'],
            "course_title": course_title,
            "course_code": course_code,
            "completion_date": data['date'],
            "filename": os.path.basename(pdf_path)
        }

    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = [
            request.files.get('pdf_file_1'),
            request.files.get('pdf_file_2'),
            request.files.get('pdf_file_3')
        ]

        verified_courses = []
        invalid_files = []

        for file in [f for f in files if f and f.filename]:
            if not file.filename.lower().endswith('.pdf'):
                invalid_files.append(file.filename)
                continue

            try:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

                result = verify_certificate(file_path)
                if result:
                    verified_courses.append(result)
                else:
                    invalid_files.append(file.filename)
            except Exception as e:
                flash(f"Error processing {file.filename}: {str(e)}", "error")
                invalid_files.append(file.filename)

        return render_template('results.html', verified_courses=verified_courses, invalid_files=invalid_files)

    return render_template('index.html')
    
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
