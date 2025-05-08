import os
from flask import Flask, render_template, request, redirect, flash, make_response
import fitz  # PyMuPDF
import re
try:
    from reportlab.pdfgen import canvas
    from io import BytesIO
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your-secret-key-here'

# Approved course titles
APPROVED_COURSES = {
    "Don't Feed The 'ish": "DFT",
    "Mandatory - Working In Partnership with BT": "BT-PART",
    "Mandatory - Living up to Our Commitments RCM Training": "RCM"
}

def is_valid_certificate(text):
    """Check basic certificate structure"""
    return all(
        elem in text for elem in [
            "BT Group", 
            "Certificate of completion",
            "has completed",
            "on"
        ]
    )

def verify_certificate(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    if not is_valid_certificate(text):
        return None

    # Extract course title
    course_match = re.search(r"has completed\s+-+\s+## (.*?)\s+on", text, re.DOTALL) or \
                  re.search(r"has completed\s+(.*?)\s+on", text, re.DOTALL)
    
    course_title = course_match.group(1).strip() if course_match else None

    if not course_title or course_title not in APPROVED_COURSES:
        return None

    # Extract completion date
    date_match = re.search(r"on\s+(\d{1,2}/\d{1,2}/\d{4})", text)
    
    return {
        "course_title": course_title,
        "course_code": APPROVED_COURSES[course_title],
        "completion_date": date_match.group(1) if date_match else "Date not available"
    }

def generate_verification_pdf(verified_courses):
    if not PDF_SUPPORT:
        raise RuntimeError("PDF generation support is not available")
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # PDF generation code remains the same as before
    # ... [rest of your PDF generation code]
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not PDF_SUPPORT:
            flash("PDF generation is not properly configured", "error")
            return redirect(request.url)

        files = [
            request.files.get('pdf_file_1'),
            request.files.get('pdf_file_2'),
            request.files.get('pdf_file_3')
        ]

        verified_courses = []
        rejected_files = []

        for file in [f for f in files if f is not None]:
            if not file.filename.lower().endswith('.pdf'):
                rejected_files.append(file.filename)
                continue

            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                result = verify_certificate(file_path)
                if result:
                    verified_courses.append(result)
                else:
                    rejected_files.append(file.filename)
            except Exception as e:
                rejected_files.append(file.filename)

        if verified_courses:
            try:
                pdf_buffer = generate_verification_pdf(verified_courses)
                response = make_response(pdf_buffer.getvalue())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=bt_certificate_verification.pdf'
                return response
            except Exception as e:
                flash(f"Failed to generate PDF: {str(e)}", "error")
                return redirect(request.url)
        else:
            flash("No valid BT certificates were found in the uploaded files", "error")
            return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
