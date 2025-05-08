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
