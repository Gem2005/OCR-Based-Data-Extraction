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

    # Save the uploaded file
    file_path = os.path.join('./uploads', file.filename)  # Save to an 'uploads' directory
    file.save(file_path)

    # Call your insert_data.py script
    try:
        result = subprocess.run(
            ['python', './scripts/insert_data.py', file_path],  # Pass the file path as an argument
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({'message': 'File processed successfully', 'output': result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error processing file', 'output': e.stderr}), 500

if __name__ == '__main__':
    # Create the uploads directory if it doesn't exist
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')
    app.run(debug=True)