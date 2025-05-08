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
            "filename": os.path.bas
