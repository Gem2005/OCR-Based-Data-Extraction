WITH patients AS (
    INSERT INTO patients (name, dob) 
    VALUES ('John Doe', '1988-01-05') 
    RETURNING id
)

-- Insert Assessment Data
INSERT INTO assessment_forms (patient_id, assessment_date, injection, exercise_therapy, difficulty_ratings, patient_changes, pain_symptoms) 
VALUES (
    (SELECT id FROM patients), 
    '2025-02-06',
    TRUE,
    FALSE,
    '{
        "bending": 3,
        "putting_on_shoes": 1,
        "sleeping": 2
    }',
    '{
        "since_last_treatment": "Not Good",
        "since_start_of_treatment": "Worse",
        "last_3_days": "Bad"
    }',
    '{
        "pain": 2,
        "numbness": 5,
        "tingling": 6
    }'
);

-- Insert Medical Assistant Data
INSERT INTO medical_assistants (patient_id, blood_pressure, heart_rate, weight, height, spo2, temperature, blood_glucose, respirations) 
VALUES ((SELECT id FROM patients), '120/80', 80, 67.5, '5''7"', 98, 98.6, 115, 16);