import streamlit as st
import requests

def main():
    st.title("DataBlind - PII Detection and Masking with RAG Chatbot")
    
    # File Upload
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
    
    if uploaded_files:
        files = {file.name: file for file in uploaded_files}
        
        # PII Customization
        st.sidebar.header("PII Customization")
        mask_email = st.sidebar.checkbox("Mask Email", value=True)
        mask_phone = st.sidebar.checkbox("Mask Phone Number", value=True)
        mask_ssn = st.sidebar.checkbox("Mask SSN", value=True)
        mask_ccn = st.sidebar.checkbox("Mask CCN", value=True)
        mask_name = st.sidebar.checkbox("Mask Name", value=True)
        mask_date = st.sidebar.checkbox("Mask Date", value=True)
        mask_location = st.sidebar.checkbox("Mask Location", value=True)
        
        if st.button("Process Files"):  
            response = requests.post(
                "http://127.0.0.1:5000/upload",
                files=[("file", file) for file in files.values()],
                data={
                    "mask_email": mask_email,
                    "mask_phone": mask_phone,
                    "mask_ssn": mask_ssn,
                    "mask_ccn": mask_ccn,
                    "mask_name": mask_name,
                    "mask_date": mask_date,
                    "mask_location": mask_location
                }
            )
            
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                st.error("Unexpected response format or empty response.")
                return

            if 'masked_file_url' in data and 'report_url' in data:
                # Single file upload
                st.success("File processed successfully!")
                st.write("Masked file: [Download Masked File](http://127.0.0.1:5000" + data['masked_file_url'] + ")")
                st.write("Report: [Download Report](http://127.0.0.1:5000" + data['report_url'] + ")")
            elif 'zip_file_url' in data:
                # Batch upload
                st.success("Files processed successfully!")
                st.write("Download ZIP: [Download ZIP File](http://127.0.0.1:5000" + data['zip_file_url'] + ")")
            else:
                st.error("Unexpected response format.")
            
    # Chatbot Interface
    st.subheader("RAG Chatbot")
    
    chatbot_query = st.text_input("Ask the chatbot:")
    
    if st.button("Submit Query"):
        response = requests.post(
            "http://127.0.0.1:5000/chatbot",
            json={"query": chatbot_query}
        )
        
        if response.status_code == 200:
            chatbot_response = response.json()
            st.write("Chatbot Response:")
            st.write(chatbot_response.get("answer", "No answer provided."))
        else:
            st.error("Error fetching response from chatbot.")

if __name__ == "__main__":
    main()
