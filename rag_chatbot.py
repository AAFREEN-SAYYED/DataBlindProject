import openai
import yaml
import pandas as pd
import os

# Load YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize OpenAI API Key
openai.api_key = config['api_key']

def process_query_with_gpt(query, current_settings, file_data):
    # Prepare file data for context
    file_summaries = ""
    for filename, df in file_data.items():
        file_summaries += f"File: {filename}\n"
        file_summaries += df.head().to_string() + "\n\n"  # Add a summary of the first few rows
    
    # Construct the messages list
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Provide detailed answers based on the uploaded files and settings."},
        {"role": "user", "content": f"File summaries:\n{file_summaries}\n\nQuery: {query}"}
    ]
    
    try:
        # Use the chat model endpoint
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the latest model available
            messages=messages
        )
        return {
            "answer": response.choices[0].message['content']
        }
    except Exception as e:
        print(f"Error processing query: {e}")
        return {"answer": "Sorry, there was an error processing your request."}
