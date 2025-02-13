from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageFilter, ImageOps
import json
import os
import re
import logging
from datetime import datetime

# Set up logging for debugging
logging.basicConfig(
    filename='ocr_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Path to Tesseract OCR (modify if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):  # No mode parameter
    try:
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        gray = image.convert("L")

        # Adaptive thresholding (more robust for varied lighting/handwriting)
        blurred = gray.filter(ImageFilter.GaussianBlur(radius=0.15))  # Increase blur radius
        thresh = blurred.point(lambda p: 255 if p > 210 else 0)  # Adjust threshold to a higher value

        # Optional: Invert if handwriting is light on a dark background
        #processed = ImageOps.invert(thresh)  # Uncomment if needed
        processed = thresh # Use thresholded image directly

        return processed
    except Exception as e:
        logging.exception(f"Error preprocessing image: {e}")
        return None

def extract_text(image, custom_config=r'--oem 1 --psm 11'):  # Optimized for handwritten text
    try:
        processed_image = preprocess_image(image)
        if processed_image is None:
            logging.error("Preprocessing failed")
            return ""
        processed_image.save("preprocessed.png")  # Save preprocessed image for debugging

        extracted_text = pytesseract.image_to_string(processed_image, config=custom_config)
        logging.debug(f"Extracted text:\n{extracted_text}")
        return extracted_text

    except Exception as e:
        logging.exception(f"Error extracting text: {e}")
        return ""


def parse_extracted_text(text, circled_values=None):
    data = {}
    try:
        # Patient Information (Improved regex for flexibility)
        name_match = re.search(r"Patient\s*Name\s*[:\-]?\s*(?P<name>[\s\S]+?)(?=\n|$)", text, re.IGNORECASE)
        dob_match = re.search(r"DOB\s*[:\-]?\s*(?P<dob>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
        data["patient_name"] = name_match.group("name").strip() if name_match else None
        data["dob"] = dob_match.group("dob").strip() if dob_match else None

        # Yes/No Fields (More robust matching)
        data["injection"] = "YES" if re.search(r"INJECTION\s*:\s*YES", text, re.IGNORECASE) else "NO"
        data["exercise_therapy"] = "YES" if re.search(r"Exercise Therapy\s*:\s*YES", text, re.IGNORECASE) else "NO"

        # Functional Abilities (Dynamic extraction, handles variations in spacing)
        difficulty_ratings = {}
        tasks = [
            "Bending or Stooping", "Putting on shoes", "Sleeping", "Standing for an hour",
            "Going up or down a flight of stairs", "Walking through a store", "Driving for an hour",
            "Preparing a meal", "Yard work", "Picking up items off the floor"
        ]
        for task in tasks:
            match = re.search(fr"{re.escape(task)}\s*[:\-]?\s*(?P<rating>[0-5])", text, re.IGNORECASE)
            if match:
                difficulty_ratings[task.lower().replace(" ", "_")] = int(match.group("rating"))
            elif circled_values and task in circled_values:
                difficulty_ratings[task.lower().replace(" ", "_")] = circled_values[task]
        data["difficulty_ratings"] = difficulty_ratings

        # Pain Symptoms (More flexible matching)
        pain_symptoms = {}
        symptoms = ["Pain", "Numbness", "Tingling", "Burning", "Tightness"]
        for symptom in symptoms:
            match = re.search(fr"{symptom}\s*[:\-]?\s*(?P<value>[0-9]+)", text, re.IGNORECASE)
            if match:
                pain_symptoms[symptom.lower()] = int(match.group("value"))
        data["pain_symptoms"] = pain_symptoms

        # Medical Assistant Data (Handles variations in spacing and optional fields)
        medical_assistant_data = {}
        ma_fields = {
            "Blood Pressure": "blood_pressure", "HR": "heart_rate", "Weight": "weight",
            "Height": "height"  # Removed SpO2, Temp, Glucose, Respirations as they are not on the form
        }
        for field, key in ma_fields.items():
            match = re.search(fr"{field}\s*[:\-]?\s*(?P<value>[\d/\.\']+)", text, re.IGNORECASE) # Added ' for feet
            if match:
                medical_assistant_data[key] = match.group("value").strip()  # Strip whitespace
            else:
            # Attempt to extract handwritten numbers using OCR
                field_match = re.search(fr"{field}\s*[:\-]?\s*(?P<value>[\s\S]+?)(?=\n|$)", text, re.IGNORECASE)
                if field_match:
                    handwritten_value = extract_text(field_match.group("value"))
                    medical_assistant_data[key] = handwritten_value.strip()

        data["medical_assistant_data"] = medical_assistant_data

        # Additional Fields (Changes in Condition)
        changes_since_last = re.search(r"Patient Changes since last treatment:\s*(?P<changes>[\s\S]+?)(?=\n|$)", text, re.IGNORECASE)
        changes_since_start = re.search(r"Patient changes since the start of treatment:\s*(?P<changes>[\s\S]+?)(?=\n|$)", text, re.IGNORECASE)
        functional_changes = re.search(r"Describe any functional changes within the last three days \(good or bad\):\s*(?P<changes>[\s\S]+?)(?=\n|$)", text, re.IGNORECASE)

        data["changes_since_last_treatment"] = changes_since_last.group("changes").strip() if changes_since_last else None
        data["changes_since_start_treatment"] = changes_since_start.group("changes").strip() if changes_since_start else None
        data["functional_changes_last_three_days"] = functional_changes.group("changes").strip() if functional_changes else None

    except Exception as e:
        logging.exception(f"Error parsing text: {e}")
        return {}  # Return empty dictionary on error for robustness

    return data

def extract_patient_data(file_path):
    """
    Main function to extract patient data from an image or PDF.
    Uses Pillow for image handling.
    """
    try:
        logging.info(f"Processing file: {file_path}")
        extracted_text = ""
        # Check if file is PDF or Image
        if file_path.lower().endswith(".pdf"):
            logging.info("Processing PDF file")
            pages = convert_from_path(file_path)
            for page_index, page in enumerate(pages):
                extracted_text += extract_text(page) + "\n"
        else:
            logging.info("Processing Image file")
            image = Image.open(file_path)
            extracted_text = extract_text(image)
        logging.debug(f"OCR Extracted Text:\n{extracted_text}")
        structured_data = parse_extracted_text(extracted_text)
        return json.dumps(structured_data, indent=2)
    except Exception as e:
        logging.exception(f"Error processing file: {e}")
        return json.dumps({})

if __name__ == "__main__":
    # Example usage:
    file_path = "uploads/Screenshot 2025-02-12 180455.png"  # Replace with your file path
    patient_data = extract_patient_data(file_path)
    print("Extracted Patient Data:")
    print(patient_data)
