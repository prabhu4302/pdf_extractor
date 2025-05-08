import os
import re
from datetime import datetime
from io import BytesIO
from flask import Flask, render_template, request, redirect, flash, make_response
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your-secret-key-here'

# Approved courses with exact matching
APPROVED_COURSES = {
    "Mandatory - Living up to Our Commitments RCM Training": "RCM",
    "Mandatory - Working In Partnership with BT": "BT-PART",
    "Don't Feed The 'ish": "DFT"
}

def extract_certificate_data(text, filename):
    """Extract data from BT certificates with robust error handling"""
    print(f"\nProcessing file: {filename}")
    print("Raw text content:")
    print("="*50)
    print(text)
    print("="*50)

    try:
        # Extract name (between certification line and first separator)
        name_match = re.search(
            r"Certificate of completion.*?This is to certify that\s*[\n-]+\s*(.*?)\s*[\n-]+\s*has completed", 
            text, 
            re.DOTALL
        )
        name = name_match.group(1).strip() if name_match else None
        print(f"Extracted name: {name}")

        # Extract course title (between separators)
        course_match = re.search(
            r"has completed\s*[\n-]+\s*(.*?)\s*[\n-]+\s*on", 
            text, 
            re.DOTALL
        )
        course = course_match.group(1).strip() if course_match else None
        print(f"Extracted course: {course}")

        # Extract date (after last separator)
        date_match = re.search(r"on\s*[\n-]*\s*(\d{1,2}/\d{1,2}/\d{4})", text)
        date = date_match.group(1) if date_match else None
        print(f"Extracted date: {date}")

        return {
            'name': name,
            'course': course,
            'date': date
        }
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        return None

def verify_certificate(pdf_path):
    try:
        print(f"\nVerifying: {pdf_path}")
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        
        # Verify required markers exist
        required_markers = [
            "BT Group",
            "Certificate of completion", 
            "This is to certify that",
            "has completed",
            "on"
        ]
        if not all(marker in text for marker in required_markers):
            print("Missing required certificate markers")
            return None

        data = extract_certificate_data(text, os.path.basename(pdf_path))
        if not data:
            print("Failed to extract certificate data")
            return None

        # Verify course title exactly matches approved courses
        course_title = data['course']
        if course_title not in APPROVED_COURSES:
            print(f"Course not in approved list: {course_title}")
            return None

        print("Verification successful!")
        return {
            "filename": os.path.basename(pdf_path),
            "name": data['name'],
            "course_title": course_title,
            "course_code": APPROVED_COURSES[course_title],
            "completion_date": data['date'],
            "status": "Verified"
        }

    except Exception as e:
        print(f"Verification error: {str(e)}")
        return None

def generate_verification_pdf(verified_courses):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(300, 770, "BT CERTIFICATE VERIFICATION REPORT")
    p.setFont("Helvetica", 12)
    p.drawCentredString(300, 745, datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Verified Certificates
    y_position = 700
    for course in verified_courses:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, course['course_title'])
        
        p.setFont("Helvetica", 10)
        p.drawString(50, y_position-20, f"Name: {course['name']}")
        p.drawString(50, y_position-40, f"Code: {course['course_code']}")
        p.drawString(50, y_position-60, f"Completed: {course['completion_date']}")
        p.drawString(50, y_position-80, f"File: {course['filename']}")
        
        y_position -= 100
    
    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(50, 30, "Official BT Verification System")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

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
                flash(f"{file.filename} is not a PDF file", "error")
                continue

            try:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                
                result = verify_certificate(file_path)
                if result:
                    verified_courses.append(result)
                    flash(f"{file.filename} verified successfully!", "success")
                else:
                    invalid_files.append(file.filename)
                    flash(f"Verification failed for {file.filename}", "error")
            except Exception as e:
                invalid_files.append(file.filename)
                flash(f"Error processing {file.filename}: {str(e)}", "error")

        if verified_courses:
            try:
                pdf_buffer = generate_verification_pdf(verified_courses)
                response = make_response(pdf_buffer.getvalue())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=bt_verification_report.pdf'
                return response
            except Exception as e:
                flash(f"Failed to generate PDF report: {str(e)}", "error")
        
        return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
