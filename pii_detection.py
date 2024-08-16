import re
import spacy

# Load SpaCy model
nlp = spacy.load('en_core_web_sm')

def detect_pii(text, mask_email=True, mask_phone=True, mask_ssn=True, mask_ccn=True, mask_name=True, mask_date=True, mask_location=True):
    # Dictionary to store detected PII entities
    pii_entities = {
        "email": [],
        "phone": [],
        "ssn": [],
        "ccn": [],
        "name": [],
        "date": [],
        "location": []
    }
    
    # Define regex patterns
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?\d[\d -]{8,}\d'
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    ccn_pattern = r'\b(?:\d[ -]{4}){3}\d{4}\b'

    if isinstance(text, str):
        # Regex-based detection
        if mask_email:
            pii_entities["email"].extend(re.findall(email_pattern, text))
        if mask_phone:
            pii_entities["phone"].extend(re.findall(phone_pattern, text))
        if mask_ssn:
            pii_entities["ssn"].extend(re.findall(ssn_pattern, text))
        if mask_ccn:
            pii_entities["ccn"].extend(re.findall(ccn_pattern, text))
        
        # SpaCy-based detection
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and mask_name:
                pii_entities["name"].append(ent.text)
            elif ent.label_ == "DATE" and mask_date:
                pii_entities["date"].append(ent.text)
            elif ent.label_ == "GPE" or ent.label_ == "LOC":
                if mask_location:
                    pii_entities["location"].append(ent.text)
    
    return pii_entities

def mask_pii(text, mask_email=True, mask_phone=True, mask_ssn=True, mask_ccn=True, mask_name=True, mask_date=True, mask_location=True):
    # Define regex patterns
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?\d[\d -]{8,}\d'
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    ccn_pattern = r'\b(?:\d[ -]{4}){3}\d{4}\b'

    # Apply regex-based masking
    if mask_email:
        text = re.sub(email_pattern, '[EMAIL MASKED]', text)
    if mask_phone:
        text = re.sub(phone_pattern, '[PHONE MASKED]', text)
    if mask_ssn:
        text = re.sub(ssn_pattern, '[SSN MASKED]', text)
    if mask_ccn:
        text = re.sub(ccn_pattern, '[CCN MASKED]', text)
    
    # Apply SpaCy-based masking
    doc = nlp(text)
    entities_to_mask = []

    for ent in doc.ents:
        if ent.label_ == "PERSON" and mask_name:
            entities_to_mask.append((ent.text, '[NAME MASKED]'))
        elif ent.label_ == "DATE" and mask_date:
            entities_to_mask.append((ent.text, '[DATE MASKED]'))
        elif ent.label_ in ["GPE", "LOC"] and mask_location:
            entities_to_mask.append((ent.text, '[LOCATION MASKED]'))

    # Replace SpaCy detected entities with their masked equivalents
    for original, masked in entities_to_mask:
        text = re.sub(re.escape(original), masked, text)

    return text
