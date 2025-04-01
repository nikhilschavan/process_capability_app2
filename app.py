import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask, render_template


# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx'}

# Helper function to calculate Cp, Cpk, Pp, Ppk
def calculate_process_capability(data, usl, lsl):
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)  # Sample standard deviation
    cp = (usl - lsl) / (6 * std_dev)
    
    # Cpk is the minimum of two values: one for the USL and one for the LSL
    cpk = min((usl - mean) / (3 * std_dev), (mean - lsl) / (3 * std_dev))
    
    # Pp and Ppk are calculated similarly using the total range of the data
    pp = (usl - lsl) / (6 * np.std(data))
    ppk = min((usl - np.mean(data)) / (3 * np.std(data)), (np.mean(data) - lsl) / (3 * np.std(data)))
    
    return cp, cpk, pp, ppk
@app.route('/')
def index():
    return render_template('index.html')  # Make sure 'index.html' exists in 'templates' folder

# Route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Retrieve USL and LSL from the form data
    usl = float(request.form['usl'])
    lsl = float(request.form['lsl'])

    # Load data from the file (CSV or Excel)
    if filename.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif filename.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    
    # Process the data
    column_data = data.iloc[:, 0]  # Assuming the data of interest is in the first column
    cp, cpk, pp, ppk = calculate_process_capability(column_data, usl, lsl)
    
    # Generate the report (charts, PDF, etc.)
    pdf_path = generate_pdf_report(data, cp, cpk, pp, ppk)
    
    # Return the URL for downloading the PDF
    return jsonify({'report_url': f'/download/{os.path.basename(pdf_path)}'})

# Route for downloading the generated report (PDF)
@app.route('/download/<filename>')
def download_report(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
