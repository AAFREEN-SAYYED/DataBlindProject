# DataBlind

**DataBlind** is a comprehensive solution for detecting and masking Personally Identifiable Information (PII) in data files. It features a Flask-based backend for processing files, a Streamlit frontend for user interaction, and integration with a RAG chatbot for querying and analysis.

## Features

- **PII Detection & Masking**: Detects and masks PII in uploaded CSV files.
- **File Processing**: Supports both single and batch file uploads.
- **Download Options**: Provides direct download links for processed files and reports.
- **Chatbot Integration**: Interact with a RAG chatbot to query and analyze uploaded data.
- **Customizable Settings**: Configure which types of PII to mask through the frontend.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/AAFREEN-SAYYED/DataBlindProject.git
   cd DataBlind
   
2. **Set Up the Environment**   
   *Create a virtual environment and install dependencies*
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   
4. **Download SpaCy Model**   
   *Install the English model for SpaCy:*
   
   ```bash
   python -m spacy download en_core_web_sm

6. **Configure API Keys**
   *Update the config.yaml file with your OpenAI API key:*
   
   ```bash
   api_key: your_openai_api_key
   
8. **Run the Application**
   
    *Start the Flask backend:*
   
    ```bash
    python app.py
    ```
    
    *Start the Streamlit frontend:*
   
    ```bash
    streamlit run ui.py
    ```

## Usage

1. *Upload Files:*
    Use the Streamlit interface to upload CSV files and customize PII masking settings.
   
2. *Process Files:*
    Click "Process Files" to start the masking process.
   
3. *Download Results:*
    Download the masked files and reports from the provided links.
   
4. *Interact with the Chatbot:*
    Ask questions related to the uploaded data through the chatbot interface.

## Contributing

Feel free to open issues or submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Contact

For questions or feedback, please reach out to *aafreens241@gmail.com*

