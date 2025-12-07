import streamlit as st
import sys
import os
import pandas as pd

# Add parent directory to path to import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core import ProtocolGenerator
from backend.ingestion import parse_document
from backend.export import export_to_pdf

st.set_page_config(page_title="ProtoScribe AI", layout="wide")

# Initialize Session State
if 'generator' not in st.session_state:
    st.session_state.generator = ProtocolGenerator()
if 'generated_sections' not in st.session_state:
    st.session_state.generated_sections = {}
if 'study_inputs' not in st.session_state:
    st.session_state.study_inputs = {}

def main():
    st.title("ProtoScribe: AI-Assisted Clinical Protocol Composer")
    # st.markdown("Turn 150-page regulatory beasts into consistent, compliant, auto-drafted protocols.")

    # Sidebar for Inputs and Config
    with st.sidebar:
        st.header("Study Setup")
        
        st.subheader("Reference Material")
        uploaded_template = st.file_uploader("Upload ICH M11 Template", type=['pdf', 'docx'])
        if uploaded_template:
            with st.spinner("Processing Template..."):
                text = parse_document(uploaded_template)
                st.session_state.generator.load_reference(text, "template")
            st.success("Template Loaded")

        uploaded_sample = st.file_uploader("Upload Pfizer Sample Protocol", type=['pdf', 'docx'])
        if uploaded_sample:
            with st.spinner("Processing Sample..."):
                text = parse_document(uploaded_sample)
                st.session_state.generator.load_reference(text, "sample")
            st.success("Sample Protocol Loaded")
        
        st.subheader("Study Inputs")
        drug_name = st.text_input("Drug Name", value="ProtoDrug-101")
        indication = st.text_input("Indication", value="Type 2 Diabetes")
        phase = st.selectbox("Phase", ["Phase I", "Phase II", "Phase III", "Phase IV"])
        
        if st.button("Initialize Study"):
            st.session_state.study_inputs = {
                "drug_name": drug_name,
                "indication": indication,
                "phase": phase
            }
            st.success("Study initialized!")
            st.session_state.generator.log_action("Study Initialized with basic inputs")

    # Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Drafting Engine", 
        "Consistency & Compliance", 
        "Sample Size", 
        "Version History",
        "Export"
    ])

    # Tab 1: Drafting Engine
    with tab1:
        st.header("Protocol Sections")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Section List")
            sections_to_generate = [
                "Background", 
                "Rationale", 
                "Objectives/Endpoints", 
                "Study Design", 
                "Inclusion/Exclusion", 
                "Safety & AE Reporting"
            ]
            selected_section = st.radio("Select Section", sections_to_generate)
            
            if st.button("Generate All Drafts"):
                with st.spinner("Drafting all sections..."):
                    for sec in sections_to_generate:
                        content = st.session_state.generator.generate_section(sec, st.session_state.study_inputs)
                        st.session_state.generated_sections[sec] = content
                st.success("All sections generated!")

        with col2:
            st.subheader(f"Editor: {selected_section}")
            
            # Check if section exists, else show placeholder or generate button
            current_content = st.session_state.generated_sections.get(selected_section, "")
            
            if not current_content:
                st.info(f"No content generated for {selected_section} yet.")
                if st.button(f"Generate {selected_section}"):
                    current_content = st.session_state.generator.generate_section(selected_section, st.session_state.study_inputs)
                    st.session_state.generated_sections[selected_section] = current_content
                    st.rerun()
            
            if current_content:
                new_content = st.text_area("Content", value=current_content, height=400, key=f"textarea_{selected_section}")
                if new_content != current_content:
                    st.session_state.generated_sections[selected_section] = new_content
                    st.session_state.generator.log_action(f"Manual edit to {selected_section}")
                    st.info("Changes saved locally.")

    # Tab 2: Consistency & Compliance
    with tab2:
        st.header("Validation Center")
        
        col_cons, col_comp = st.columns(2)
        
        with col_cons:
            st.subheader("Consistency Checks")
            if st.button("Run Consistency Check"):
                issues = st.session_state.generator.check_consistency(st.session_state.generated_sections)
                if issues:
                    for issue in issues:
                        st.warning(f"**{issue['severity']}**: {issue['message']}")
                else:
                    st.success("No consistency issues found.")

        with col_comp:
            st.subheader("Compliance Flags (M11)")
            if st.button("Run Compliance Check"):
                flags = st.session_state.generator.check_compliance(st.session_state.generated_sections)
                if flags:
                    for flag in flags:
                        st.error(f"**{flag['severity']}**: {flag['message']}")
                else:
                    st.success("Protocol appears compliant with M11 structure.")

        st.subheader("Regulatory Simulation")
        if st.button("Simulate Regulatory Change (FDA Guidance Update)"):
            st.info("Simulating new FDA guidance on Inclusion Criteria...")
            st.markdown("""
            **Adaptive Revision Suggestion:**
            *Current Text:* "Patients aged 18-65."
            *New Guidance:* "Enrollment of older adults (>65) is encouraged unless safety data excludes."
            *Suggestion:* Update Inclusion Criteria to "Patients aged 18 and older..."
            """)

    # Tab 3: Sample Size
    with tab3:
        st.header("Sample Size Estimator")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            alpha = st.number_input("Alpha (Significance Level)", value=0.05)
        with c2:
            power = st.number_input("Power (1-Beta)", value=0.8)
        with c3:
            effect_size = st.number_input("Effect Size", value=0.5)
            
        if st.button("Calculate N"):
            n = st.session_state.generator.calculate_sample_size(alpha, power, effect_size)
            st.metric(label="Estimated Sample Size (per arm)", value=n)
            st.caption("Based on simplified Z-test approximation for demo purposes.")

    # Tab 4: Version History
    with tab4:
        st.header("Audit Trail")
        df_log = st.session_state.generator.get_audit_history()
        st.dataframe(df_log, use_container_width=True)

    # Tab 5: Export
    with tab5:
        st.header("Export Protocol")
        export_format = st.selectbox("Format", ["PDF", "DOCX", "XML (CDISC)"])
        
        if st.button(f"Generate Export ({export_format})"):
            if export_format == "PDF":
                pdf_bytes = export_to_pdf(st.session_state.generated_sections, st.session_state.study_inputs)
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name="protocol_draft.pdf",
                    mime="application/pdf"
                )
            else:
                 st.info(f"{export_format} export is a placeholder in this demo.")


if __name__ == "__main__":
    main()
