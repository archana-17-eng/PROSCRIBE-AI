# ProtoScribe AI

ProtoScribe is an AI-powered drafting and validation engine for clinical protocols. It helps turn regulatory templates into consistent, compliant, auto-drafted protocols.

## Features

1.  **Document Ingestion:** Upload ICH M11 templates and sample protocols (PDF/DOCX).
2.  **Auto-Drafting:** Generates key protocol sections (Background, Objectives, Design, etc.) based on inputs.
3.  **Consistency Checks:** Flags mismatches between sections (e.g., Inclusion Criteria vs Study Design).
4.  **Compliance Checks:** Ensures required M11 fields are present.
5.  **Sample Size Estimator:** Basic calculator for study power/sample size.
6.  **Audit Trail:** Tracks all changes and generations.
7.  **Export:** Download the drafted protocol as PDF.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application:**
    ```bash
    streamlit run frontend/app.py
    ```

## Structure

*   `frontend/`: Contains the Streamlit user interface (`app.py`).
*   `backend/`: Contains the application logic.
    *   `core.py`: Main logic for generation, checks, and state management.
    *   `ingestion.py`: parsing logic for PDF and DOCX files.
    *   `export.py`: PDF generation logic.
*   `data/`: Directory for storing local data (if needed).


