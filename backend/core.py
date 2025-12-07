import pandas as pd
import random
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

class ProtocolGenerator:
    def __init__(self):
        self.audit_log = []
        self.reference_material = {
            "template": "",
            "sample": ""
        }
        
        # Initialize the Chat Model using the pattern provided
        # LangChain's ChatGoogleGenerativeAI automatically looks for GOOGLE_API_KEY in os.environ
        self.llm = ChatGroq(
        # model="llama-3.1-8b-instant",
        model = "llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # other params...
)
        

    def log_action(self, action, user="System"):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user,
            "action": action
        }
        self.audit_log.append(entry)
        return entry

    def load_reference(self, text, ref_type="template"):
        self.reference_material[ref_type] = text
        self.log_action(f"Loaded {ref_type} reference material")

    def _call_llm(self, prompt, system_prompt="You are a helpful assistant for clinical protocol writing."):
        if not self.llm:
            return "Error: GOOGLE_API_KEY not configured."
        
        try:
            # LangChain invocation with System and Human messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def generate_section(self, section_name, inputs):
        self.log_action(f"Generated section: {section_name}")
        
        if not self.llm:
            # Fallback to mock if no client
            base_text = f"## {section_name}\n\n(Mock Generation - Set GOOGLE_API_KEY to enable AI)\n"
            return base_text + f"Content for {section_name} based on {inputs.get('drug_name')}..."

        # Construct Prompt
        system_prompt = """You are an expert clinical research associate and medical writer specializing in clinical trial protocols. 
Your task is to draft specific sections of a clinical protocol based on the ICH M11 guideline and provided study inputs.
Use professional, regulatory-compliant language."""

        context_prompt = f"""
        task: Draft the '{section_name}' section for a clinical trial protocol.
        
        Study Inputs:
        - Drug Name: {inputs.get('drug_name')}
        - Indication: {inputs.get('indication')}
        - Phase: {inputs.get('phase')}
        
        Reference Material (Excerpt):
        {self.reference_material['sample'][:2000] if self.reference_material['sample'] else "No sample protocol provided."}
        
        Instructions:
        - Write a comprehensive draft for the '{section_name}' section.
        - Ensure consistency with the study inputs.
        - If reference material is provided, adopt a similar tone and structure but adapt it strictly to the new study inputs.
        """
        
        return self._call_llm(context_prompt, system_prompt)

    def check_consistency(self, sections):
        issues = []
        if not self.llm:
             # Mock logic checks
            if "Inclusion/Exclusion" in sections and "Study Design" in sections:
                inc_exc = sections["Inclusion/Exclusion"]
                study_design = sections["Study Design"]
                if "18 and 65" in inc_exc and "children" in study_design.lower():
                     issues.append({"severity": "Critical", "message": "Inclusion criteria specifies adults (18-65), but Study Design mentions children."})
            return issues

        # LLM based consistency check
        prompt = f"""
        Analyze the following protocol sections for consistency issues (e.g., contradictions in population, objectives vs endpoints, etc.).
        
        Sections:
        {str(sections)}
        
        Return a JSON list of issues found. If none, return empty list.
        Format: [{{"severity": "Warning/Critical", "message": "Description"}}]
        """
        
        analysis = self._call_llm(prompt, "You are a QA auditor for clinical protocols.")
        
        # Naive parsing or just returning a generic issue with the analysis content if it looks like an issue
        if "No issues found" not in analysis and len(analysis) > 10:
             issues.append({"severity": "AI Review", "message": analysis})
             
        return issues

    def check_compliance(self, sections):
        flags = []
        required_fields = ["Primary Objective", "Secondary Objective", "Adverse events"]
        
        # Hybrid: Keep the basic keyword check, it's fast and reliable for absolute basics
        content = " ".join(sections.values())
        for field in required_fields:
            if field not in content:
                flags.append({"severity": "Critical", "message": f"Missing required M11 field: {field}"})
        
        return flags

    def calculate_sample_size(self, alpha=0.05, power=0.8, effect_size=0.5):
        # Mock calculation using basic formula concepts or returning pre-calculated
        try:
            n = (2 * (1.96 + 0.84)**2) / (float(effect_size)**2) # Simplified Z-test approximation
            return int(n)
        except ZeroDivisionError:
            return 0

    def get_audit_history(self):
        return pd.DataFrame(self.audit_log)
if __name__ == "__main__":
    generator = ProtocolGenerator()
    print(generator._call_llm("What is the capital of France?"))