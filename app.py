import re
import fitz  # PyMuPDF

def verify_certificate(pdf_path):
    """
    Verify a BT Group certificate with the exact format shown in the sample.
    Returns extracted data if valid, None if invalid.
    """
    try:
        # Open PDF and extract text
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        # Debug: Print extracted text
        print("Extracted text from PDF:")
        print("="*50)
        print(text)
        print("="*50)

        # Verify required elements exist
        required_elements = [
            "BT Group",
            "Certificate of completion",
            "This is to certify that",
            "has completed",
            "on"
        ]
        
        for element in required_elements:
            if element not in text:
                print(f"Missing required element: {element}")
                return None

        # Extract data using precise pattern matching
        pattern = re.compile(
            r"BT Group\s+Certificate of completion\s+This is to certify that\s+-+\s+(.*?)\s+-+\s+has completed\s+-+\s+(.*?)\s+-+\s+on\s+-+\s+(\d{1,2}/\d{1,2}/\d{4})",
            re.DOTALL
        )
        
        match = pattern.search(text)
        if not match:
            print("Certificate format does not match expected pattern")
            return None

        name = match.group(1).strip()
        course = match.group(2).strip()
        date = match.group(3).strip()

        # Verify course title
        approved_courses = {
            "Don't Feed The 'ish": "DFT",
            "Mandatory - Living up to Our Commitments RCM Training": "RCM",
            "Mandatory - Working In Partnership with BT": "BT-PART"
        }
        
        if course not in approved_courses:
            print(f"Course not in approved list: {course}")
            return None

        # Return extracted data
        return {
            "name": name,
            "course_title": course,
            "course_code": approved_courses[course],
            "completion_date": date,
            "status": "Verified"
        }

    except Exception as e:
        print(f"Verification error: {str(e)}")
        return None

# Example usage:
result = verify_certificate("CertificateOfCompletion (2).pdf")
if result:
    print("\nCertificate is valid!")
    print("Extracted data:")
    for key, value in result.items():
        print(f"{key}: {value}")
else:
    print("\nCertificate verification failed")
