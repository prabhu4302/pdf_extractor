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

# Debug mode - set to False in production
DEBUG = True

# Course patterns that match your exact certificates
APPROVED_COURSES = {
    "Mandatory - Living up to Our Commitments RCM Training": "RCM",
    "Mandatory - Working In Partnership with BT": "BT-PART", 
    "Don't Feed The 'ish": "DFT"
}

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

def extract_certificate_data(text, filename):
    """Extract data from certificate with detailed debugging"""
    debug_print(f"\nProcessing file: {filename}")
    debug_print("Full text content:")
    debug_print("="*50)
    debug_print(text)
    debug_print("="*50)

    # Try multiple patterns to handle variations
    patterns = [
        # Primary pattern for standard BT certificates
        {
            'name': r"Certificate of completion.*?This is to certify that\s*\n*\s*-+\s*\n*\s*(.*?)\s*\n*\s*has completed",
            'course': r"has completed\s*\n*\s*-+\s*\n*\s*(.*?)\s*\n*\s*on",
            'date': r"on\s*\n*\s*(\d{1,2}/\d{1,2}/\d{4})"
        },
        # Fallback pattern
        {
            'course': r"has completed\s*(.*?)\s*on",
            'date': r"on\s*(\d{1,2}/\d{1,2}/\d{4})"
        }
    ]

    for i, pattern in enumerate(patterns, 1):
        debug_print(f"\nTrying pattern {i}:")
        try:
            # Extract name (if pattern includes it)
            name = None
            if 'name' in pattern:
                name_match = re.search(pattern['name'], text, re.DOTALL)
                if name_match:
                    name = name_match.group(1).strip()
                    debug_print(f"Name found: {name}")
                else:
                    debug_print("Name not found with this pattern")
                    continue

            # Extract course title
            course_match = re.search(pattern['course'], text, re.DOTALL)
            if not course_match:
                debug_print("Course title not found with this pattern")
                continue
            
            course_title = course_match.group(1).strip()
            debug_print(f"Course title found: {course_title}")

            # Extract date
            date_match = re.search(pattern['date'], text)
            if not date_match:
                debug_print("Date not found with this pattern")
                continue
            
            date = date_match.group(1)
            debug_print(f"Date found: {date}")

            return {
                'name': name,
                'course': course_title,
                'date': date
            }

        except Exception as e:
            debug_print(f"Error with pattern {i}: {str(e)}")
            continue

    debug_print("No patterns matched the certificate content")
    return None

def verify_certificate(pdf_path):
    try:
        debug_print(f"\nStarting verification for: {pdf_path}")
        
        # Open PDF and extract text
        doc = fitz.open(pdf_path)
        text = ""
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text("text")
            debug_print(f"\nPage {page_num} content:")
            debug_print(page_text)
            text += page_text + "\n"

        # Basic validation
        required_markers = ["BT Group", "Certificate of completion"]
        missing_markers = [marker for marker in required_markers if marker not in text]
        
        if missing_markers:
            debug_print(f"Missing required markers: {', '.join(missing_markers)}")
            return None

        # Extract certificate data
        data = extract_certificate_data(text, os.path.basename(pdf_path))
        if not data:
            debug_print("Failed to extract certificate data")
            return None

        # Verify course title
        course_title = data['course']
        debug_print(f"Verifying course title: {course_title}")

        if course_title not in APPROVED_COURSES:
            debug_print("Course title not in approved courses list")
            debug_print(f"Approved courses: {list(APPROVED_COURSES.keys())}")
            return None

        debug_print("Certificate verification successful!")
        return {
            "filename": os.path.basename(pdf_path),
            "course_title": course_title,
            "course_code": APPROVED_COURSES[course_title],
            "completion_date": data['date'],
            "status": "Verified"
        }

    except Exception as e:
        debug_print(f"Verification error: {str(e)}")
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
        p.drawString(50, y_position-20, f"Code: {course['course_code']}")
        p.drawString(50, y_position-40, f"Completed: {course['completion_date']}")
        p.drawString(50, y_position-60, f"File: {course['filename']}")
        
        y_position -= 80
    
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
