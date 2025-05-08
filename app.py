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

# Enhanced course patterns with flexible matching
APPROVED_COURSES = {
    r"(?i)(mandatory\s*-?\s*)?living up to our commitments rcm training": {
        "code": "RCM",
        "type": "Compliance"
    },
    r"(?i)(mandatory\s*-?\s*)?working in partnership with bt": {
        "code": "BT-PART",
        "type": "Partnership"
    },
    r"(?i)don'?t feed the '?ish": {
        "code": "DFT",
        "type": "Ethics"
    }
}

def extract_certificate_data(text):
    """Improved extraction with multiple pattern attempts"""
    # Try different patterns to handle variations
    patterns = [
        # Standard BT format
        {
            'course': re.compile(r"has completed\s+(?:the course)?\s*([^-]+-?\s*.+?)\s+on", 
                               re.DOTALL|re.IGNORECASE),
            'date': re.compile(r"on\s+(\d{1,2}/\d{1,2}/\d{4})")
        },
        # Alternative format
        {
            'course': re.compile(r"completed\s+(?:the )?(training|course) in\s+(.+?)\s+on",
                               re.DOTALL|re.IGNORECASE),
            'date': re.compile(r"on\s+(\d{1,2}[\/-]\d{1,2}[\/-]\d{4})")
        }
    ]

    for pattern in patterns:
        try:
            course_match = pattern['course'].search(text)
            date_match = pattern['date'].search(text)
            
            if course_match:
                # Clean the course title
                course_title = course_match.group(1).replace('\n', ' ').strip()
                return {
                    'course': course_title,
                    'date': date_match.group(1) if date_match else None
                }
        except Exception:
            continue
    
    return None

def verify_certificate(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        
        # Basic validation
        if not all(x in text for x in ["BT Group", "Certificate of completion"]):
            return None

        data = extract_certificate_data(text)
        if not data:
            return None

        # Find matching course
        course_title = data['course']
        course_info = None
        
        for pattern, info in APPROVED_COURSES.items():
            if re.fullmatch(pattern, course_title, re.IGNORECASE):
                course_info = info
                break

        if not course_info:
            return None

        return {
            "filename": os.path.basename(pdf_path),
            "course_title": course_title,
            "course_code": course_info["code"],
            "course_type": course_info["type"],
            "completion_date": data['date'] or "Date not available",
            "status": "Verified"
        }

    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
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
        p.drawString(50, y_position-20, f"Code: {course['course_code']} | Type: {course['course_type']}")
        p.drawString(50, y_position-40, f"Completed: {course['completion_date']}")
        p.drawString(50, y_position-60, f"File: {course['filename']}")
        
        y_position -= 80
        if y_position < 100:  # Add new page if running out of space
            p.showPage()
            y_position = 750
    
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
                invalid_files.append(file.filename)
                print(f"Error processing {file.filename}: {str(e)}")

        if verified_courses:
            try:
                pdf_buffer = generate_verification_pdf(verified_courses)
                response = make_response(pdf_buffer.getvalue())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=bt_verification_report.pdf'
                return response
            except Exception as e:
                flash(f"Failed to generate PDF: {str(e)}", "error")
        
        if invalid_files:
            flash("Some files couldn't be verified:", "warning")
            for filename in invalid_files:
                flash(f"- {filename}", "warning")
        
        return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
