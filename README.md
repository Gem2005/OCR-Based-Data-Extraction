# OCR-Based Patient Data Extraction with Supabase

## 📌 Overview

This project extracts **handwritten and printed text** from **patient assessment forms** in **PDF and image formats** using **Tesseract OCR**. The extracted data is then stored in a **Supabase PostgreSQL database** for further analysis.

### 🔮 Key Features:
- **Uses Tesseract OCR** to extract both **handwritten and printed text**.
- **Handles PDFs and images automatically**.
- **Parses structured data** (Patient details, symptoms, assessments, etc.).
- **Stores extracted data into a Supabase PostgreSQL database**.
- **JSON-based storage for flexible querying and analysis**.
- **File Upload System with Flask Web Interface**.

---

## 📂 Project Structure

```
OCR-Based-Patient-Data-Extraction
│── data/                     # Folder for storing raw PDFs & images
│── scripts/
│   ├── insert_data.py         # Parses extracted data & inserts into Supabase
│   ├── ocr_extraction.py      # Extracts text from PDFs & images using Tesseract OCR
│   ├── setup_database.py      # Creates necessary tables in Supabase
│── sql/
│   ├── database_schema.sql    # SQL script for creating tables in Supabase
│   ├── insert_sample_data.sql # SQL script for inserting test data
│── templates/
│   ├── index.html             # HTML page for file upload
│── uploads/                   # Folder for uploaded files
│── .env                       # Environment variables for database connection
│── .env.sample                # Sample environment variable file
│── main.py                    # Flask app for file upload & processing
│── ocr_debug.log              # Log file for debugging OCR extraction
│── preprocessed.png           # Example preprocessed image
│── README.md                  # Project documentation
│── requirements.txt           # Required Python dependencies
```

---

## 🛠 Installation Guide

### **1️⃣ Prerequisites**
Ensure you have the following installed:

- **Python 3.8+**
- **Supabase (PostgreSQL Database)**
- **Tesseract OCR**
- **pip (Python package manager)**
- **Supabase Python SDK (`supabase-py`)**
- **Flask for web interface**

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/OCR-Based-Patient-Data-Extraction.git
cd OCR-Based-Patient-Data-Extraction
```

### **3️⃣ Install Dependencies**
Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate     # For Windows
```

Then install the required dependencies:

```bash
pip install -r requirements.txt
```

### **4️⃣ Install Tesseract OCR**
**Windows**  
Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki).  
After installation, update `pytesseract.pytesseract_cmd` in your script.

**Mac**  
```bash
brew install tesseract
```

**Linux**  
```bash
sudo apt install tesseract-ocr
```

### **5️⃣ Setup Supabase Database**
#### **➤ Configure `.env` File**
Create a `.env` file in the project root:

```ini
dbname=your_database
user=your_username
password=your_password
host=your_host
port=your_port
```

#### **➤ Run Database Setup**
```bash
python scripts/setup_database.py
```

---

## 🚀 How to Use the Project

### **1️⃣ Upload and Process Files via Web Interface**
Start the Flask server:
```bash
python main.py
```
Visit `http://127.0.0.1:5000/` in your browser, upload a file, and process it.

#### **Access the Web Interface**
```bash
http://127.0.0.1:5000/
```

### **2️⃣ Extract Data from PDF or Image Manually**
```bash
python scripts/insert_data.py data/sample_form.pdf
```

### **3️⃣ Verify Inserted Data in Supabase**
```sql
SELECT * FROM patients;
SELECT * FROM assessment_forms;
```

### **4️⃣ Debug OCR Extraction**
If extraction has issues, check `ocr_debug.log` for errors.

---

## 🔍 Web Interface (`main.py`)
This Flask app allows users to upload PDFs and images through a web page. The uploaded file is processed by `insert_data.py`.

```python
from flask import Flask, request, jsonify, render_template
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join('./uploads', file.filename)
    file.save(file_path)

    try:
        result = subprocess.run(
            ['python', './scripts/insert_data.py', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({'message': 'File processed successfully', 'output': result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error processing file', 'output': e.stderr}), 500

if __name__ == '__main__':
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')
    app.run(debug=True)
```

---

## ⚠️ Limitations & Future Improvements

### 🔴 Current Limitations
1. **Handwriting Accuracy**  
   - Tesseract struggles with heavily cursive or unclear handwriting.  
   - 📌 **Solution**: Integrate deep learning-based OCR models.

2. **JSON-Based Queries Performance**  
   - JSONB queries in PostgreSQL can be slow if dataset grows large.  
   - 📌 **Solution**: Optimize database queries & indexing.

3. **Limited GUI Support**  
   - Currently, operations are **CLI-based**.  
   - 📌 **Solution**: Build a React or Flask-based web UI.

4. **Multi-Language Support**  
   - Works best with **English documents**.  
   - 📌 **Solution**: Use **Google Vision OCR API** for other languages.

---

## 🎯 Conclusion
This project automates **handwritten & printed OCR extraction** from patient forms, reducing **manual data entry time** and **storing structured data in Supabase for easy retrieval**. It also includes a **Flask-based web interface** for file uploads and processing. 🚀

