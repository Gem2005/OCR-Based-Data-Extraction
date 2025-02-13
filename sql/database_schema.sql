-- Create Patients Table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL
);

-- Create Assessment Forms Table (Stores Patient Functional Assessment)
CREATE TABLE assessment_forms (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(id) ON DELETE CASCADE,
    assessment_date DATE NOT NULL,
    injection BOOLEAN NOT NULL,
    exercise_therapy BOOLEAN NOT NULL,
    difficulty_ratings JSONB NOT NULL,
    patient_changes JSONB NOT NULL,
    pain_symptoms JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Medical Assistant Table (Stores MA Inputs)
CREATE TABLE medical_assistants (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(id) ON DELETE CASCADE,
    blood_pressure VARCHAR(20),
    heart_rate INT,
    weight DECIMAL(5,2),
    height VARCHAR(10),
    spo2 INT,
    temperature DECIMAL(4,1),
    blood_glucose INT,
    respirations INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add Index for Faster JSON Queries
CREATE INDEX idx_assessment_json ON assessment_forms USING GIN (difficulty_ratings, patient_changes, pain_symptoms);
