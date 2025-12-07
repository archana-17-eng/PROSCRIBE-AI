import io
from pypdf import PdfReader
from docx import Document

def parse_document(uploaded_file):
    """
    Parses an uploaded file (PDF or DOCX) and returns text content.
    """
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    text = ""
    
    try:
        if file_type == 'pdf':
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif file_type == 'docx':
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            return f"Unsupported file type: {file_type}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
        
    return text


