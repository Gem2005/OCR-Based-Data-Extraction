import psycopg2
import json
import os
from dotenv import load_dotenv
import sys
from ocr_extraction import extract_patient_data  # Universal OCR function
import datetime

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("dbname"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "port": os.getenv("port"),
    "sslmode": "require"
}

def insert_assessment_data(file_path):
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Extract text & structured data from the file (image or PDF)
        form_data_json = extract_patient_data(file_path)
        form_data = json.loads(form_data_json)

        # Extract patient details
        patient_name = form_data.get("patient_name")
        dob = form_data.get("dob")

        if not patient_name or not dob:
            print("Error: Missing patient name or date of birth. Skipping insertion.")
            return

        # Insert patient if not exists
        cursor.execute(
            """
            INSERT INTO patients (name, dob)
            VALUES (%s, %s)
            ON CONFLICT (name, dob) DO NOTHING
            RETURNING id
            """,
            (patient_name, dob)
        )
        patient_id = cursor.fetchone()
        
        if patient_id is None:
            cursor.execute(
                """
                SELECT id FROM patients WHERE name = %s AND dob = %s
                """,
                (patient_name, dob)
            )
            patient_id = cursor.fetchone()[0]
        else:
            patient_id = patient_id[0]

        # Extract & validate assessment data
        assessment_date_str = form_data.get("date")
        assessment_date = (
            datetime.datetime.strptime(assessment_date_str, "%Y-%m-%d").date()
            if assessment_date_str else datetime.date.today()
        )

        injection = form_data.get("injection") == "YES"
        exercise_therapy = form_data.get("exercise_therapy") == "YES"
        difficulty_ratings = json.dumps(form_data.get("difficulty_ratings", {}))
        pain_symptoms = json.dumps(form_data.get("pain_symptoms", {}))
        medical_assistant_data = form_data.get("medical_assistant_data", {})

        # Insert into assessment_forms table
        cursor.execute(
            """
            INSERT INTO assessment_forms (patient_id, assessment_date, injection, exercise_therapy, difficulty_ratings, pain_symptoms)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (patient_id, assessment_date, injection, exercise_therapy, difficulty_ratings, pain_symptoms)
        )

        # Insert into medical_assistants table
        cursor.execute(
            """
            INSERT INTO medical_assistants (patient_id, blood_pressure, heart_rate, weight, height, spo2, temperature, blood_glucose, respirations)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                patient_id,
                medical_assistant_data.get("blood_pressure"),
                medical_assistant_data.get("heart_rate"),
                medical_assistant_data.get("weight"),
                medical_assistant_data.get("height"),
                medical_assistant_data.get("spo2"),
                medical_assistant_data.get("temperature"),
                medical_assistant_data.get("blood_glucose"),
                medical_assistant_data.get("respirations"),
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()
        print("Data inserted successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # Get file path from command-line argument
        insert_assessment_data(file_path)
    else:
        print("No file path provided. Usage: python insert_data.py <file_path>")
