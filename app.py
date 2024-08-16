from flask import Flask, request, send_file, jsonify, abort
import pandas as pd
import os
import zipfile
import io
from pii_detection import detect_pii, mask_pii
from rag_chatbot import process_query_with_gpt
from report_generator import generate_report

app = Flask(__name__)

# Ensure the downloads directory exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')
@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('file')
    print("Received files:", files)
    masked_files = []
    reports = []

    # PII Customization settings
    settings = {
        "mask_email": request.form.get('mask_email', 'true').lower() == 'true',
        "mask_phone": request.form.get('mask_phone', 'true').lower() == 'true',
        "mask_ssn": request.form.get('mask_ssn', 'true').lower() == 'true',
        "mask_ccn": request.form.get('mask_ccn', 'true').lower() == 'true',
        "mask_name": request.form.get('mask_name', 'true').lower() == 'true',
        "mask_date": request.form.get('mask_date', 'true').lower() == 'true',
        "mask_location": request.form.get('mask_location', 'true').lower() == 'true'
    }

    if len(files) == 1:
        # Single file upload
        file = files[0]
        df = pd.read_csv(file)
        
        # Initialize the PII data dictionary
        pii_data = {
            "email": [],
            "phone": [],
            "ssn": [],
            "ccn": [],
            "name": [],
            "date": [],
            "location": []
        }
        
        # Apply detection for each column in the dataframe
        for column in df.columns:
            for value in df[column]:
                detected_pii = detect_pii(
                    str(value),
                    **settings
                )
                
                # Populate pii_data dictionary
                for pii_type, values in detected_pii.items():
                    pii_data[pii_type].extend(values)
        
        # Apply masking
        masked_df = df.apply(lambda col: col.map(lambda x: mask_pii(
            x, **settings
        ) if isinstance(x, str) else x) if col.dtype == 'object' else col)
        
        # Save the masked file
        masked_filename = f"masked_{file.filename}"
        masked_filepath = f"downloads/{masked_filename}"
        masked_df.to_csv(masked_filepath, index=False)
        masked_files.append(masked_filepath)
        
        # Generate the PII report
        report_path = generate_report(pii_data)
        reports.append(report_path)
        
        return jsonify({
            "masked_file_url": f"/download?filename={masked_filename}",
            "report_url": f"/download?filename={os.path.basename(report_path)}"
        }), 200

    else:
        # Batch upload
        for file in files:
            df = pd.read_csv(file)
            
            # Initialize the PII data dictionary
            pii_data = {
                "email": [],
                "phone": [],
                "ssn": [],
                "ccn": [],
                "name": [],
                "date": [],
                "location": []
            }
            
            # Apply detection for each column in the dataframe
            for column in df.columns:
                for value in df[column]:
                    detected_pii = detect_pii(
                        str(value),
                        **settings
                    )
                    
                    # Populate pii_data dictionary
                    for pii_type, values in detected_pii.items():
                        pii_data[pii_type].extend(values)
            
            # Apply masking
            masked_df = df.apply(lambda col: col.map(lambda x: mask_pii(
                x, **settings
            ) if isinstance(x, str) else x) if col.dtype == 'object' else col)
            
            # Save the masked file
            masked_filename = f"masked_{file.filename}"
            masked_filepath = f"downloads/{masked_filename}"
            masked_df.to_csv(masked_filepath, index=False)
            masked_files.append(masked_filepath)
            
            # Generate the PII report
            report_path = generate_report(pii_data)
            reports.append(report_path)
        
        # Create a ZIP file containing all masked files and reports
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            seen_files = set()
            for file_path in masked_files + reports:
                base_name = os.path.basename(file_path)
                # Ensure unique names
                unique_name = base_name
                counter = 1
                while unique_name in seen_files:
                    unique_name = f"{base_name}_{counter}"
                    counter += 1
                seen_files.add(unique_name)
                zip_file.write(file_path, unique_name)
        zip_buffer.seek(0)

        # Save the zip buffer to a file
        zip_filepath = "downloads/masked_files_and_reports.zip"
        with open(zip_filepath, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        return jsonify({
            "zip_file_url": "/download?filename=masked_files_and_reports.zip"
        }), 200

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    filepath = f"downloads/{filename}"
    
    if not os.path.exists(filepath):
        return abort(404, description="File not found")
    
    return send_file(filepath, as_attachment=True)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    query = request.json.get("query")
    
    # Example current settings, you should retrieve this from your application state
    current_settings = {
        "mask_email": True,
        "mask_phone": True,
        "mask_ssn": True,
        "mask_ccn": True,
        "mask_name": True,
        "mask_date": True,
        "mask_location": True
    }
    
    file_data = {}
    for file in os.listdir('downloads'):
        if file.startswith('masked_'):
            filepath = os.path.join('downloads', file)
            if file.endswith('.zip'):
                # Handle ZIP files
                with zipfile.ZipFile(filepath, 'r') as zip_file:
                    for zip_info in zip_file.infolist():
                        with zip_file.open(zip_info.filename) as file_content:
                            df = pd.read_csv(file_content)
                            file_data[zip_info.filename] = df
            else:
                # Handle single files
                df = pd.read_csv(filepath)
                file_data[file] = df  # Include the full DataFrame for context
    
    response = process_query_with_gpt(query, current_settings, file_data)
    return jsonify(response), 200

@app.route('/reprocess', methods=['POST'])
def reprocess_file():
    # Reprocess the file with updated settings
    settings = {
        "mask_email": request.form.get('mask_email', 'true').lower() == 'true',
        "mask_phone": request.form.get('mask_phone', 'true').lower() == 'true',
        "mask_ssn": request.form.get('mask_ssn', 'true').lower() == 'true',
        "mask_ccn": request.form.get('mask_ccn', 'true').lower() == 'true',
        "mask_name": request.form.get('mask_name', 'true').lower() == 'true',
        "mask_date": request.form.get('mask_date', 'true').lower() == 'true',
        "mask_location": request.form.get('mask_location', 'true').lower() == 'true'
    }
    
    # Assuming the filename comes from a request parameter
    filename = request.form.get('filename', 'example.csv')
    filepath = f"downloads/{filename}"
    if not os.path.exists(filepath):
        return abort(404, description="File not found")

    df = pd.read_csv(filepath)
    
    # Apply masking with new settings
    masked_df = df.apply(lambda col: col.map(lambda x: mask_pii(
        x, **settings
    ) if isinstance(x, str) else x) if col.dtype == 'object' else col)
    
    masked_filename = f"masked_{filename}"
    masked_filepath = f"downloads/{masked_filename}"
    masked_df.to_csv(masked_filepath, index=False)
    
    # Generate updated report
    report_path = generate_report({})  # Update report generation as needed
    
    return jsonify({
        "masked_filename": masked_filename,
        "report_filename": os.path.basename(report_path)
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
