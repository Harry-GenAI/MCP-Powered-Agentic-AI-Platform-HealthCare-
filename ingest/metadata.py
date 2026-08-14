import re

# ============================================================
# Extract Metadata Value
# ============================================================
def extract_value(text:str, pattern:str)->str:

    match = re.search(pattern, text, flags=re.IGNORECASE)

    if match:
        return match.group(1).strip()
    
    return ""

# ============================================================
# Document Classification
# ============================================================
def classify_document(file_name:str)->str:
    
    name = file_name.lower()

    if "clinical" in name:
        return "clinical_knowledge"
    
    if "policy" in name:
        return "medical_policy"

    if "operations" in name:
        return "hospital_operations"
    
    if "admission" in name:
        return "admission_report"

    if "discharge" in name:
        return "discharge_report"
    
    if "scanned" in name:
        return "scanned_docuemnt"
    
    return "general"


# ============================================================
# Metadata Builder
# ============================================================
def build_metadata(
    pdf_path,
    text:str,
    has_tables:bool,
    has_images:bool,
    is_ocr:bool
) -> dict:

    document_type = classify_document(
        pdf_path.name
    )

    metadata = {
        "source": pdf_path.name,
        "document_type":document_type,
        "department":"general",
        "access_level":"general",
        "patient_id":"",
        "doctor_id":"",
        "document_version":"",
        "ingestion_type": "ocr" if is_ocr else "digital",
        "has_tables":has_tables,
        "has_images":has_images
    }
    
    #Department / Access classification
    if document_type == "clinical":

        metadata["department"] = "clinical"
        metadata["access_level"] = "doctor"
    
    
    if document_type == "medical_policy":
        
        metadata["department"] = "administration"
    
    
    if document_type == "hospital_operations":

        metadata["department"] = "operations"
    
    elif document_type in ("admission_report", "discharge_report", "scanned_document"):

        metadata["department"] = "patient_services"
        metadata["access_level"] = "restricted_clinical"
    

    #Patien ID
    metadata["patient_id"] = extract_value(
        text,
        r"Patient\s*ID\s*[:=|]\s*([A-Za-z0-9\-]+)"
    )


    #Doctor ID
    metadata["doctor_id"] = extract_value(
        text,
        r"(?:Doctor|Attending Doctor)"
        r"\s*ID?\s*[:=|]\s*"
        r"([A-Za-z0-9\-]+)"
    )


    #Document Version
    metadata["document_version"] = extract_value(
        text,
        r"(?:version|document\s+version)"
        r"\s*[:=|]\s*([0-9.]+)"
    )

    return metadata
