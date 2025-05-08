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

# Course patterns that match your exact certificates
APPROVED_COURSES = {
    r"Mandatory - Living up to Our Commitments RCM Training": "RCM",
    r"Mandatory - Working In Partnership with BT": "BT-PART", 
    r"Don't Feed The 'ish": "DFT"
}

def extract_certificate_data(text):
    """Extract data from your specific certificate format"""
    # Pattern that matches your exact certificate structure
    pattern = re.compile(
        r"Certificate of completion.*?"
        r"This is to certify that\s*\n*\s*---*\s*\n*\s*(.*?)\s*\n*\s*"
        r"has completed\s*\n*\s*---*\s*\n*\s*(.*?)\s*\n*\s*"
        r"on\s*\n*\s*(\d{1,2}/\d{1,2}/\d{4})",
        re.DOTALL
    )
    
    match = pattern.search(text)
    if match:
        return {
            'name': match.group(1).strip(),
            'course': match.group(2).strip(),
            'date': match.group(3).strip()
        }
    return None

def verify_certificate(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")  # Use "text" extraction mode
        
        # Check for required certificate markers
        if not all(x in text for x in ["BT Group", "Certificate of completion"]):
            return None

        data = extract_certificate_data(text)
        if not data:
            return None

        # Exact course title matching
        course_title = data['course']
        if course_title not in APPROVED_COURSES:
            return None

        return {
            "filename": os.path.basename(pdf_path),
            "course_title": course_title,
            "course_code": APPROVED_COURSES[course_title],
            "completion_date": data['date'],
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
                    print(f"Verification failed for: {file.filename}")
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
            flash("Verification failed for:", "error")
            for filename in invalid_files:
                flash(f"- {filename}", "error")
        
        return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
