import pandas as pd
import os
from datetime import datetime

def generate_report(pii_data):
    # Create DataFrame for the report
    report_df = pd.DataFrame({
        "Type": [],
        "Value": []
    })
    
    for pii_type, values in pii_data.items():
        report_df = pd.concat([report_df, pd.DataFrame({
            "Type": pii_type,
            "Value": values
        })])
    
    # Ensure the downloads directory exists
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    # Generate a timestamp to append to the filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = "pii_report"
    report_path = f"downloads/{base_filename}_{timestamp}.csv"
    
    # Ensure no filename collision by checking if the file already exists
    counter = 1
    while os.path.exists(report_path):
        report_path = f"downloads/{base_filename}_{timestamp}_{counter}.csv"
        counter += 1
    
    # Save the DataFrame to the CSV file
    report_df.to_csv(report_path, index=False)
    
    return report_path
