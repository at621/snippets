"""
AI-Assisted Clinical Study Report (CSR) Drafting Agent

This module implements an agent for managing the AI-assisted drafting of clinical study reports
with appropriate human oversight throughout the process. The system follows a structured workflow:

1. Data Input and Retrieval
2. AI-Generated Content Creation
3. Human Oversight and Refinement
4. Quality Control and Compliance
5. Finalization and Approval
6. Efficiency Metrics and Outcomes

The agent coordinates these steps while maintaining audit trails, ensuring regulatory compliance,
and tracking efficiency metrics.
"""

import os
import time
import json
import logging
import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Set, Tuple, Any
from dataclasses import dataclass, field
import pandas as pd
from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("csr_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CSRAgent")

class DocumentStatus(Enum):
    """Status tracking for CSR sections and the overall document."""
    NOT_STARTED = "not_started"
    DRAFT_IN_PROGRESS = "draft_in_progress"
    DRAFT_COMPLETED = "draft_completed"
    HUMAN_REVIEW_IN_PROGRESS = "human_review_in_progress"
    HUMAN_REVIEW_COMPLETED = "human_review_completed"
    QC_IN_PROGRESS = "qc_in_progress"
    QC_COMPLETED = "qc_completed"
    FINAL_APPROVAL_IN_PROGRESS = "final_approval_in_progress"
    APPROVED = "approved"


@dataclass
class StudyData:
    """Container for all the study data needed to draft the CSR."""
    protocol: Dict = field(default_factory=dict)
    sap: Dict = field(default_factory=dict)
    efficacy_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    safety_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    demographics: pd.DataFrame = field(default_factory=pd.DataFrame)
    tables_listings_figures: Dict = field(default_factory=dict)
    additional_data: Dict = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate that all required data is present and correctly formatted."""
        # Basic validation to ensure required data is available
        required_protocol_fields = {"title", "objectives", "design", "population", "treatments", "endpoints"}
        if not self.protocol or not required_protocol_fields.issubset(set(self.protocol.keys())):
            logger.error(f"Protocol missing required fields: {required_protocol_fields - set(self.protocol.keys())}")
            return False
            
        if self.efficacy_data.empty:
            logger.error("Efficacy data is missing")
            return False
            
        if self.safety_data.empty:
            logger.error("Safety data is missing")
            return False
            
        return True


@dataclass
class CSRSection:
    """Represents a section of the CSR document."""
    title: str
    content: str = ""
    status: DocumentStatus = DocumentStatus.NOT_STARTED
    data_sources: List[str] = field(default_factory=list)
    ai_generated: bool = False
    review_comments: List[Dict] = field(default_factory=list)
    qc_comments: List[Dict] = field(default_factory=list)
    approval_status: Dict = field(default_factory=dict)
    version_history: List[Dict] = field(default_factory=list)


@dataclass
class CSRDocument:
    """Represents the entire CSR document with all sections."""
    title: str
    sections: Dict[str, CSRSection] = field(default_factory=dict)
    status: DocumentStatus = DocumentStatus.NOT_STARTED
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_modified: datetime.datetime = field(default_factory=datetime.datetime.now)
    metrics: Dict = field(default_factory=dict)
    
    def get_section_by_title(self, title: str) -> Optional[CSRSection]:
        """Retrieve a section by its title."""
        return self.sections.get(title)
    
    def add_section(self, section: CSRSection) -> None:
        """Add a new section to the document."""
        self.sections[section.title] = section
        self.last_modified = datetime.datetime.now()
        
    def update_section(self, title: str, content: str, status: DocumentStatus) -> None:
        """Update an existing section."""
        if title in self.sections:
            # Save old version in history
            old_version = {
                "content": self.sections[title].content,
                "status": self.sections[title].status,
                "timestamp": datetime.datetime.now()
            }
            self.sections[title].version_history.append(old_version)
            
            # Update with new content
            self.sections[title].content = content
            self.sections[title].status = status
            self.last_modified = datetime.datetime.now()
        else:
            raise ValueError(f"Section {title} not found")
    
    def update_status(self) -> None:
        """Update overall document status based on section statuses."""
        section_statuses = [section.status for section in self.sections.values()]
        
        if all(status == DocumentStatus.APPROVED for status in section_statuses):
            self.status = DocumentStatus.APPROVED
        elif any(status == DocumentStatus.FINAL_APPROVAL_IN_PROGRESS for status in section_statuses):
            self.status = DocumentStatus.FINAL_APPROVAL_IN_PROGRESS
        elif all(status == DocumentStatus.QC_COMPLETED for status in section_statuses):
            self.status = DocumentStatus.QC_COMPLETED
        elif any(status == DocumentStatus.QC_IN_PROGRESS for status in section_statuses):
            self.status = DocumentStatus.QC_IN_PROGRESS
        elif all(status == DocumentStatus.HUMAN_REVIEW_COMPLETED for status in section_statuses):
            self.status = DocumentStatus.HUMAN_REVIEW_COMPLETED
        elif any(status == DocumentStatus.HUMAN_REVIEW_IN_PROGRESS for status in section_statuses):
            self.status = DocumentStatus.HUMAN_REVIEW_IN_PROGRESS
        elif all(status == DocumentStatus.DRAFT_COMPLETED for status in section_statuses):
            self.status = DocumentStatus.DRAFT_COMPLETED
        elif any(status == DocumentStatus.DRAFT_IN_PROGRESS for status in section_statuses):
            self.status = DocumentStatus.DRAFT_IN_PROGRESS
        else:
            self.status = DocumentStatus.NOT_STARTED
            
        self.last_modified = datetime.datetime.now()


class DataInputHandler:
    """Handles the input and organization of study data for the CSR."""
    
    def __init__(self):
        self.study_data = StudyData()
        
    def load_protocol(self, file_path: str) -> None:
        """Load protocol data from a file."""
        # In a real system, this would parse the protocol document
        logger.info(f"Loading protocol from {file_path}")
        try:
            # Placeholder for actual protocol parsing logic
            # This would extract structured data from the protocol document
            with open(file_path, 'r') as f:
                protocol_data = json.load(f)
            self.study_data.protocol = protocol_data
            logger.info("Protocol loaded successfully")
        except Exception as e:
            logger.error(f"Error loading protocol: {str(e)}")
            raise
            
    def load_statistical_analysis_plan(self, file_path: str) -> None:
        """Load SAP data from a file."""
        logger.info(f"Loading SAP from {file_path}")
        try:
            # Placeholder for actual SAP parsing logic
            with open(file_path, 'r') as f:
                sap_data = json.load(f)
            self.study_data.sap = sap_data
            logger.info("SAP loaded successfully")
        except Exception as e:
            logger.error(f"Error loading SAP: {str(e)}")
            raise
            
    def load_efficacy_data(self, file_path: str) -> None:
        """Load efficacy data from a CSV or similar file."""
        logger.info(f"Loading efficacy data from {file_path}")
        try:
            self.study_data.efficacy_data = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.study_data.efficacy_data)} efficacy data records")
        except Exception as e:
            logger.error(f"Error loading efficacy data: {str(e)}")
            raise
            
    def load_safety_data(self, file_path: str) -> None:
        """Load safety data from a CSV or similar file."""
        logger.info(f"Loading safety data from {file_path}")
        try:
            self.study_data.safety_data = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.study_data.safety_data)} safety data records")
        except Exception as e:
            logger.error(f"Error loading safety data: {str(e)}")
            raise
            
    def load_demographics(self, file_path: str) -> None:
        """Load demographics data from a CSV or similar file."""
        logger.info(f"Loading demographics from {file_path}")
        try:
            self.study_data.demographics = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.study_data.demographics)} demographic records")
        except Exception as e:
            logger.error(f"Error loading demographics: {str(e)}")
            raise
            
    def load_tables_listings_figures(self, directory_path: str) -> None:
        """Load TLFs from a directory."""
        logger.info(f"Loading TLFs from {directory_path}")
        try:
            tlf_data = {}
            # In a real system, this would scan and parse TLF files
            # Placeholder for TLF loading logic
            for filename in os.listdir(directory_path):
                if filename.endswith('.json'):  # Example format
                    with open(os.path.join(directory_path, filename), 'r') as f:
                        tlf_data[filename] = json.load(f)
            
            self.study_data.tables_listings_figures = tlf_data
            logger.info(f"Loaded {len(tlf_data)} TLF items")
        except Exception as e:
            logger.error(f"Error loading TLFs: {str(e)}")
            raise
            
    def validate_all_data(self) -> bool:
        """Validate that all necessary data is loaded and properly formatted."""
        return self.study_data.validate()
    
    def organize_data_for_section(self, section_title: str) -> Dict:
        """Organize relevant data for a specific CSR section."""
        # Map section titles to required data sources
        section_data_map = {
            "Introduction": {
                "protocol": ["title", "objectives", "background"],
                "sap": ["analysis_populations"]
            },
            "Methods": {
                "protocol": ["design", "population", "treatments", "endpoints", "procedures"],
                "sap": ["statistical_methods", "analysis_sets", "sample_size"]
            },
            "Results": {
                "data": ["efficacy_data", "demographics"],
                "tlf": ["efficacy_tables", "demographic_tables"]
            },
            "Safety Results": {
                "data": ["safety_data"],
                "tlf": ["safety_tables", "ae_listings"]
            },
            "Discussion and Conclusion": {
                "protocol": ["objectives", "endpoints"],
                "data": ["efficacy_data", "safety_data"],
                "tlf": ["summary_tables"]
            }
        }
        
        # Get data mapping for the requested section
        data_mapping = section_data_map.get(section_title, {})
        
        # Collect relevant data
        section_data = {}
        
        # Extract protocol data
        if "protocol" in data_mapping:
            section_data["protocol"] = {k: self.study_data.protocol.get(k) 
                                       for k in data_mapping["protocol"] 
                                       if k in self.study_data.protocol}
                                       
        # Extract SAP data
        if "sap" in data_mapping:
            section_data["sap"] = {k: self.study_data.sap.get(k) 
                                  for k in data_mapping["sap"] 
                                  if k in self.study_data.sap}
                                  
        # Extract dataframe data
        if "data" in data_mapping:
            section_data["data"] = {}
            if "efficacy_data" in data_mapping["data"] and not self.study_data.efficacy_data.empty:
                section_data["data"]["efficacy"] = self.study_data.efficacy_data.to_dict(orient="records")
            if "safety_data" in data_mapping["data"] and not self.study_data.safety_data.empty:
                section_data["data"]["safety"] = self.study_data.safety_data.to_dict(orient="records")
            if "demographics" in data_mapping["data"] and not self.study_data.demographics.empty:
                section_data["data"]["demographics"] = self.study_data.demographics.to_dict(orient="records")
                
        # Extract TLF data
        if "tlf" in data_mapping:
            section_data["tlf"] = {}
            for tlf_type in data_mapping["tlf"]:
                # Find TLFs with matching prefixes
                matching_tlfs = {k: v for k, v in self.study_data.tables_listings_figures.items() 
                               if k.startswith(tlf_type)}
                if matching_tlfs:
                    section_data["tlf"][tlf_type] = matching_tlfs
        
        return section_data


class ContentGenerator:
    """Handles AI-assisted generation of CSR content based on study data."""
    
    def __init__(self, api_key: str, model: str = "claude-3-7-sonnet-20250219"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        
    def generate_section_content(self, section_title: str, section_data: Dict, template: Optional[str] = None) -> str:
        """Generate content for a CSR section using the AI model."""
        logger.info(f"Generating content for section: {section_title}")
        
        # Create a system prompt with detailed instructions
        system_prompt = """
        You are an AI assistant for clinical study report (CSR) drafting. Your task is to draft a specific section of a 
        CSR based on the provided data and guidelines. Follow these requirements:
        
        1. Use formal scientific writing appropriate for regulatory documents
        2. Maintain objectivity in describing results
        3. Only include information supported by the provided data
        4. Follow standard CSR structure and terminology
        5. Format text appropriately with headings, lists, and paragraphs
        6. Include appropriate references to tables and figures
        7. Maintain consistency in terminology
        8. DO NOT make up or infer data not present in the inputs
        """
        
        # Add template guidance if provided
        if template:
            system_prompt += f"\n\nUse the following template structure for this section:\n{template}"
        
        # Create the user prompt with section information and data
        user_prompt = f"Draft the '{section_title}' section of a clinical study report using the following data:\n\n"
        
        # Format the data for the prompt
        for data_type, data in section_data.items():
            user_prompt += f"--- {data_type.upper()} DATA ---\n"
            user_prompt += json.dumps(data, indent=2) + "\n\n"
        
        # Add specific guidance based on section type
        section_guidance = {
            "Introduction": "Include study background, rationale, objectives, and a brief overview of the study design.",
            "Methods": "Detail the study design, population, treatments, endpoints, and statistical methods.",
            "Results": "Present the efficacy results objectively with appropriate statistical context.",
            "Safety Results": "Summarize safety findings, focusing on adverse events, laboratory assessments, and other safety parameters.",
            "Discussion and Conclusion": "Interpret the results in context of the objectives, without overstating conclusions."
        }
        
        if section_title in section_guidance:
            user_prompt += f"GUIDANCE: {section_guidance[section_title]}\n\n"
        
        user_prompt += "Please draft this section in a format ready for inclusion in the CSR."
        
        try:
            # Call the Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Extract the generated content
            content = response.content[0].text
            logger.info(f"Successfully generated content for {section_title} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    def refine_content(self, original_content: str, feedback: str) -> str:
        """Refine content based on human feedback."""
        logger.info("Refining content based on feedback")
        
        system_prompt = """
        You are an AI assistant helping to refine a clinical study report (CSR) section. 
        Your task is to revise the provided content based on the feedback from human reviewers.
        Follow these guidelines:
        
        1. Address all issues mentioned in the feedback
        2. Maintain the scientific accuracy and regulatory compliance
        3. Preserve the original structure unless specifically instructed otherwise
        4. Ensure all data references are accurate
        5. Maintain consistent terminology
        6. Return the complete revised content, not just the changes
        """
        
        user_prompt = f"""
        Here is the original content:
        
        ---ORIGINAL CONTENT---
        {original_content}
        
        Here is the feedback from reviewers:
        
        ---FEEDBACK---
        {feedback}
        
        Please revise the content addressing all the feedback points and return the complete revised content.
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            revised_content = response.content[0].text
            logger.info(f"Successfully refined content ({len(revised_content)} chars)")
            return revised_content
        except Exception as e:
            logger.error(f"Error refining content: {str(e)}")
            raise


class HumanReviewManager:
    """Handles the workflow for human review and refinement of AI-generated content."""
    
    def __init__(self, document: CSRDocument, content_generator: ContentGenerator):
        self.document = document
        self.content_generator = content_generator
        
    def assign_section_for_review(self, section_title: str, reviewer_id: str) -> None:
        """Assign a section to a human reviewer."""
        if section_title in self.document.sections:
            section = self.document.sections[section_title]
            # Only assign if the section is ready for review
            if section.status == DocumentStatus.DRAFT_COMPLETED:
                section.status = DocumentStatus.HUMAN_REVIEW_IN_PROGRESS
                section.approval_status["reviewer_id"] = reviewer_id
                section.approval_status["assigned_at"] = datetime.datetime.now()
                
                logger.info(f"Section '{section_title}' assigned to reviewer {reviewer_id}")
            else:
                logger.warning(f"Cannot assign section '{section_title}' for review - not in DRAFT_COMPLETED status")
        else:
            logger.error(f"Section '{section_title}' not found in document")
            
    def submit_review_feedback(self, section_title: str, reviewer_id: str, feedback: str, 
                               approved: bool = False) -> None:
        """Submit feedback from a human reviewer for a section."""
        if section_title in self.document.sections:
            section = self.document.sections[section_title]
            
            # Verify the reviewer is assigned to this section
            if section.approval_status.get("reviewer_id") != reviewer_id:
                logger.warning(f"Reviewer {reviewer_id} not assigned to section '{section_title}'")
                return
                
            # Record the feedback
            comment = {
                "reviewer_id": reviewer_id,
                "timestamp": datetime.datetime.now(),
                "feedback": feedback,
                "approved": approved
            }
            section.review_comments.append(comment)
            
            if approved:
                # Mark as review completed if approved
                section.status = DocumentStatus.HUMAN_REVIEW_COMPLETED
                section.approval_status["review_completed_at"] = datetime.datetime.now()
                logger.info(f"Review completed and approved for section '{section_title}'")
            else:
                # If not approved, use AI to refine the content based on feedback
                try:
                    revised_content = self.content_generator.refine_content(section.content, feedback)
                    
                    # Save old version in history
                    old_version = {
                        "content": section.content,
                        "status": section.status,
                        "timestamp": datetime.datetime.now()
                    }
                    section.version_history.append(old_version)
                    
                    # Update with refined content
                    section.content = revised_content
                    
                    logger.info(f"Content refined for section '{section_title}' based on review feedback")
                except Exception as e:
                    logger.error(f"Error refining content: {str(e)}")
                    # Keep status as in-review if refinement fails
                    return
            
            # Update document status
            self.document.update_status()
        else:
            logger.error(f"Section '{section_title}' not found in document")
            
    def get_review_status(self) -> Dict:
        """Get the current review status of all sections."""
        status = {}
        for title, section in self.document.sections.items():
            status[title] = {
                "status": section.status.value,
                "reviewer": section.approval_status.get("reviewer_id", "unassigned"),
                "comments": len(section.review_comments),
                "last_updated": section.approval_status.get("review_completed_at", "not completed")
            }
        return status


class QualityControlManager:
    """Handles quality control checks on the CSR document."""
    
    def __init__(self, document: CSRDocument, study_data: StudyData):
        self.document = document
        self.study_data = study_data
        self.regulatory_checklist = self._load_regulatory_checklist()
        
    def _load_regulatory_checklist(self) -> Dict:
        """Load the regulatory compliance checklist (e.g., based on ICH E3 guidelines)."""
        # In a real system, this would load from a configuration file
        # Here we provide a simplified example
        return {
            "required_sections": [
                "Title Page", "Synopsis", "Table of Contents", "Introduction",
                "Study Objectives", "Investigational Plan", "Study Population",
                "Efficacy Evaluation", "Safety Evaluation", "Discussion and Conclusions",
                "Tables, Figures, and Graphs"
            ],
            "regulatory_requirements": {
                "ICH_E3_compliance": "The CSR must follow ICH E3 structure",
                "data_transparency": "All analyses must be traceable to protocol and SAP",
                "patient_privacy": "No patient identifiers should be included",
                "adverse_event_reporting": "All AEs must be reported according to MedDRA"
            }
        }
        
    def assign_qc_review(self, section_title: str, qc_reviewer_id: str) -> None:
        """Assign a section for QC review."""
        if section_title in self.document.sections:
            section = self.document.sections[section_title]
            # Only assign if the section has completed human review
            if section.status == DocumentStatus.HUMAN_REVIEW_COMPLETED:
                section.status = DocumentStatus.QC_IN_PROGRESS
                section.approval_status["qc_reviewer_id"] = qc_reviewer_id
                section.approval_status["qc_assigned_at"] = datetime.datetime.now()
                
                logger.info(f"Section '{section_title}' assigned to QC reviewer {qc_reviewer_id}")
            else:
                logger.warning(f"Cannot assign section '{section_title}' for QC - not in HUMAN_REVIEW_COMPLETED status")
        else:
            logger.error(f"Section '{section_title}' not found in document")
    
    def perform_automated_qc_checks(self, section_title: str) -> Dict:
        """Perform automated QC checks on a section."""
        if section_title not in self.document.sections:
            logger.error(f"Section '{section_title}' not found in document")
            return {"error": "Section not found"}
            
        section = self.document.sections[section_title]
        content = section.content
        
        qc_results = {
            "spelling_grammar": self._check_spelling_grammar(content),
            "data_consistency": self._check_data_consistency(content, section_title),
            "template_compliance": self._check_template_compliance(content, section_title),
            "regulatory_compliance": self._check_regulatory_compliance(content, section_title),
            "overall_status": "passed"  # Default status, will be updated based on checks
        }
        
        # Update overall status if any check failed
        if any(result["status"] == "failed" for result in qc_results.values() if isinstance(result, dict)):
            qc_results["overall_status"] = "failed"
            
        return qc_results
        
    def _check_spelling_grammar(self, content: str) -> Dict:
        """Check spelling and grammar in the content."""
        # In a real system, this would use a spelling/grammar checker
        # Here we provide a placeholder implementation
        issues = []
        # Placeholder for actual checks
        # issues = spell_grammar_checker.check(content)
        
        return {
            "status": "passed" if len(issues) == 0 else "failed",
            "issues": issues
        }
        
    def _check_data_consistency(self, content: str, section_title: str) -> Dict:
        """Check consistency of data mentioned in the content."""
        # In a real system, this would extract numbers/data from the text
        # and compare with the source data
        # Here we provide a placeholder implementation
        issues = []
        
        # Example check for data consistency
        if section_title == "Results" and self.study_data.efficacy_data is not None:
            # Placeholder for actual consistency checks
            # e.g., comparing numbers in text against actual data values
            pass
            
        return {
            "status": "passed" if len(issues) == 0 else "failed",
            "issues": issues
        }
        
    def _check_template_compliance(self, content: str, section_title: str) -> Dict:
        """Check if the content follows the required template structure."""
        # Placeholder implementation
        issues = []
        
        # Example checks
        if section_title == "Methods":
            if "Study Design" not in content:
                issues.append("Missing 'Study Design' subsection in Methods")
            if "Statistical Methods" not in content:
                issues.append("Missing 'Statistical Methods' subsection in Methods")
                
        return {
            "status": "passed" if len(issues) == 0 else "failed",
            "issues": issues
        }
        
    def _check_regulatory_compliance(self, content: str, section_title: str) -> Dict:
        """Check compliance with regulatory requirements."""
        # Placeholder implementation
        issues = []
        
        # Example check for patient identifiers (which should not be present)
        # In a real system, this would use regex or NER to find potential PHI
        # patient_id_pattern = re.compile(r"\b\d{6}\b")  # Example pattern for patient IDs
        # if patient_id_pattern.search(content):
        #     issues.append("Possible patient identifier found in content")
            
        return {
            "status": "passed" if len(issues) == 0 else "failed",
            "issues": issues
        }
        
    def submit_qc_feedback(self, section_title: str, qc_reviewer_id: str, feedback: str, 
                          approved: bool = False) -> None:
        """Submit QC feedback for a section."""
        if section_title in self.document.sections:
            section = self.document.sections[section_title]
            
            # Verify the QC reviewer is assigned to this section
            if section.approval_status.get("qc_reviewer_id") != qc_reviewer_id:
                logger.warning(f"QC reviewer {qc_reviewer_id} not assigned to section '{section_title}'")
                return
                
            # Record the QC feedback
            comment = {
                "qc_reviewer_id": qc_reviewer_id,
                "timestamp": datetime.datetime.now(),
                "feedback": feedback,
                "approved": approved
            }
            section.qc_comments.append(comment)
            
            if approved:
                # Mark as QC completed if approved
                section.status = DocumentStatus.QC_COMPLETED
                section.approval_status["qc_completed_at"] = datetime.datetime.now()
                logger.info(f"QC completed and approved for section '{section_title}'")
            else:
                # If not approved, section goes back to human review
                section.status = DocumentStatus.HUMAN_REVIEW_IN_PROGRESS
                section.approval_status["returned_from_qc_at"] = datetime.datetime.now()
                logger.info(f"Section '{section_title}' returned to human review with QC feedback")
            
            # Update document status
            self.document.update_status()
        else:
            logger.error(f"Section '{section_title}' not found in document")


class FinalApprovalManager:
    """Handles the final approval process for the CSR document."""
    
    def __init__(self, document: CSRDocument):
        self.document = document
        
    def initiate_approval_process(self) -> bool:
        """Start the final approval process if all sections have passed QC."""
        # Check if all sections have completed QC
        sections_ready = all(section.status == DocumentStatus.QC_COMPLETED 
                            for section in self.document.sections.values())
                            
        if not sections_ready:
            logger.warning("Cannot initiate approval process - not all sections have completed QC")
            return False
            
        # Update document status
        self.document.status = DocumentStatus.FINAL_APPROVAL_IN_PROGRESS
        
        # Update all sections to approval in progress
        for section in self.document.sections.values():
            section.status = DocumentStatus.FINAL_APPROVAL_IN_PROGRESS
            
        logger.info("Final approval process initiated")
        return True
        
    def assign_approver(self, approver_id: str, approver_role: str) -> None:
        """Assign a stakeholder as an approver."""
        if self.document.status != DocumentStatus.FINAL_APPROVAL_IN_PROGRESS:
            logger.warning("Cannot assign approver - document not in FINAL_APPROVAL_IN_PROGRESS status")
            return
            
        if "approvers" not in self.document.metrics:
            self.document.metrics["approvers"] = []
            
        approver = {
            "id": approver_id,
            "role": approver_role,
            "assigned_at": datetime.datetime.now(),
            "status": "pending"
        }
        
        self.document.metrics["approvers"].append(approver)
        logger.info(f"Assigned {approver_role} {approver_id} as approver")
        
    def record_approval(self, approver_id: str, comments: str = "") -> None:
        """Record approval from a stakeholder."""
        if "approvers" not in self.document.metrics:
            logger.warning("No approvers assigned yet")
            return
            
        # Find the approver
        for approver in self.document.metrics["approvers"]:
            if approver["id"] == approver_id:
                approver["status"] = "approved"
                approver["approval_time"] = datetime.datetime.now()
                approver["comments"] = comments
                logger.info(f"Recorded approval from {approver_id}")
                break
        else:
            logger.warning(f"Approver {approver_id} not found")
            return
            
        # Check if all approvers have approved
        all_approved = all(approver["status"] == "approved" 
                          for approver in self.document.metrics["approvers"])
                          
        if all_approved:
            # Mark document as approved
            self.document.status = DocumentStatus.APPROVED
            
            # Mark all sections as approved
            for section in self.document.sections.values():
                section.status = DocumentStatus.APPROVED
                
            logger.info("All approvals received - document is now APPROVED")
            
    def get_approval_status(self) -> Dict:
        """Get the current approval status."""
        if "approvers" not in self.document.metrics:
            return {"status": "not_started", "approvers": []}
            
        approvers_status = [{
            "id": approver["id"],
            "role": approver["role"],
            "status": approver["status"],
            "approval_time": approver.get("approval_time", None)
        } for approver in self.document.metrics["approvers"]]
        
        return {
            "status": self.document.status.value,
            "approvers": approvers_status
        }
        
    def finalize_document(self) -> str:
        """Finalize the approved document and prepare for submission."""
        if self.document.status != DocumentStatus.APPROVED:
            logger.warning("Cannot finalize document - not in APPROVED status")
            return ""
            
        # In a real system, this would compile the final document
        # Here we simply concatenate all sections
        final_content = ""
        
        # Get a sorted list of sections in the correct order
        section_order = [
            "Title Page", "Synopsis", "Table of Contents", "Introduction",
            "Study Objectives", "Investigational Plan", "Study Population",
            "Efficacy Evaluation", "Safety Evaluation", "Discussion and Conclusions"
        ]
        
        # Add ordered sections first
        for section_title in section_order:
            if section_title in self.document.sections:
                section = self.document.sections[section_title]
                final_content += f"# {section_title}\n\n{section.content}\n\n"
                
        # Add any remaining sections not in the predefined order
        for title, section in self.document.sections.items():
            if title not in section_order:
                final_content += f"# {title}\n\n{section.content}\n\n"
                
        # Record finalization
        self.document.metrics["finalized_at"] = datetime.datetime.now()
        self.document.metrics["final_document_length"] = len(final_content)
        
        logger.info("Document finalized successfully")
        return final_content


class MetricsTracker:
    """Tracks and reports efficiency metrics for the CSR drafting process."""
    
    def __init__(self, document: CSRDocument):
        self.document = document
        self.start_time = datetime.datetime.now()
        
        # Initialize metrics
        if "efficiency_metrics" not in self.document.metrics:
            self.document.metrics["efficiency_metrics"] = {
                "start_time": self.start_time,
                "section_metrics": {},
                "review_cycles": {},
                "time_savings": {},
                "quality_metrics": {}
            }
            
    def track_section_completion(self, section_title: str, is_ai_generated: bool, 
                                generation_time: float) -> None:
        """Track the completion of a section draft."""
        metrics = self.document.metrics["efficiency_metrics"]
        
        if "section_metrics" not in metrics:
            metrics["section_metrics"] = {}
            
        # Record section metrics
        metrics["section_metrics"][section_title] = {
            "ai_generated": is_ai_generated,
            "generation_time": generation_time,
            "completion_time": datetime.datetime.now(),
            "word_count": len(self.document.sections[section_title].content.split())
        }
        
    def track_review_cycle(self, section_title: str, cycle_number: int, 
                          review_time: float, issues_found: int) -> None:
        """Track a review cycle for a section."""
        metrics = self.document.metrics["efficiency_metrics"]
        
        if "review_cycles" not in metrics:
            metrics["review_cycles"] = {}
            
        if section_title not in metrics["review_cycles"]:
            metrics["review_cycles"][section_title] = []
            
        # Record review cycle
        metrics["review_cycles"][section_title].append({
            "cycle": cycle_number,
            "time": review_time,
            "issues": issues_found,
            "completion_time": datetime.datetime.now()
        })
        
    def calculate_time_savings(self, traditional_writing_time: Dict[str, float]) -> None:
        """Calculate estimated time savings compared to traditional writing.
        
        Args:
            traditional_writing_time: Dict mapping section titles to estimated hours
                                     for traditional writing
        """
        metrics = self.document.metrics["efficiency_metrics"]
        
        if "section_metrics" not in metrics:
            logger.warning("Cannot calculate time savings - no section metrics available")
            return
            
        total_actual_time = 0
        total_traditional_time = 0
        
        for section_title, section_metrics in metrics["section_metrics"].items():
            if section_title in traditional_writing_time:
                # Convert to hours for comparison
                actual_time = section_metrics["generation_time"] / 3600
                traditional_time = traditional_writing_time[section_title]
                
                # Calculate savings
                time_saved = traditional_time - actual_time
                
                # Update totals
                total_actual_time += actual_time
                total_traditional_time += traditional_time
                
                # Record per-section savings
                if "time_savings" not in metrics:
                    metrics["time_savings"] = {}
                    
                metrics["time_savings"][section_title] = {
                    "actual_hours": actual_time,
                    "traditional_hours": traditional_time,
                    "hours_saved": time_saved,
                    "percentage_saved": (time_saved / traditional_time) * 100 if traditional_time > 0 else 0
                }
        
        # Record total savings
        if total_traditional_time > 0:
            metrics["time_savings"]["total"] = {
                "actual_hours": total_actual_time,
                "traditional_hours": total_traditional_time,
                "hours_saved": total_traditional_time - total_actual_time,
                "percentage_saved": ((total_traditional_time - total_actual_time) / total_traditional_time) * 100
            }
            
    def track_quality_metric(self, metric_name: str, value: Any) -> None:
        """Track a quality metric."""
        metrics = self.document.metrics["efficiency_metrics"]
        
        if "quality_metrics" not in metrics:
            metrics["quality_metrics"] = {}
            
        metrics["quality_metrics"][metric_name] = {
            "value": value,
            "recorded_at": datetime.datetime.now()
        }
        
    def generate_metrics_report(self) -> Dict:
        """Generate a comprehensive metrics report."""
        metrics = self.document.metrics["efficiency_metrics"]
        
        # Calculate elapsed time
        end_time = datetime.datetime.now()
        elapsed_time = (end_time - self.start_time).total_seconds() / 3600  # in hours
        
        # Calculate section statistics
        section_stats = {
            "total_sections": len(metrics.get("section_metrics", {})),
            "ai_generated_sections": sum(1 for m in metrics.get("section_metrics", {}).values() if m.get("ai_generated")),
            "total_words": sum(m.get("word_count", 0) for m in metrics.get("section_metrics", {}).values())
        }
        
        # Calculate review statistics
        review_stats = {
            "total_review_cycles": sum(len(cycles) for cycles in metrics.get("review_cycles", {}).values()),
            "avg_issues_per_review": 0,
            "avg_review_time": 0
        }
        
        all_cycles = [cycle for cycles in metrics.get("review_cycles", {}).values() for cycle in cycles]
        if all_cycles:
            review_stats["avg_issues_per_review"] = sum(cycle.get("issues", 0) for cycle in all_cycles) / len(all_cycles)
            review_stats["avg_review_time"] = sum(cycle.get("time", 0) for cycle in all_cycles) / len(all_cycles)
        
        # Calculate time savings
        time_savings = metrics.get("time_savings", {}).get("total", {})
        
        # Create the report
        report = {
            "report_date": datetime.datetime.now(),
            "total_elapsed_time_hours": elapsed_time,
            "section_statistics": section_stats,
            "review_statistics": review_stats,
            "time_savings": time_savings,
            "quality_metrics": metrics.get("quality_metrics", {})
        }
        
        return report


class CSRDraftingAgent:
    """Main agent class coordinating the entire CSR drafting workflow."""
    
    def __init__(self, title: str, api_key: str, model: str = "claude-3-7-sonnet-20250219"):
        self.document = CSRDocument(title=title)
        self.data_handler = DataInputHandler()
        self.content_generator = ContentGenerator(api_key=api_key, model=model)
        self.human_review_manager = HumanReviewManager(self.document, self.content_generator)
        self.metrics_tracker = None  # Initialized after data is loaded
        
        logger.info(f"CSR Drafting Agent initialized for document: {title}")
        
    def load_study_data(self, data_sources: Dict[str, str]) -> bool:
        """Load all study data from the specified sources.
        
        Args:
            data_sources: Dict mapping data types to file paths
                        e.g., {"protocol": "path/to/protocol.json", 
                               "efficacy_data": "path/to/efficacy.csv"}
        
        Returns:
            bool: True if data loading was successful, False otherwise
        """
        logger.info("Loading study data from sources")
        
        try:
            # Load data by type
            if "protocol" in data_sources:
                self.data_handler.load_protocol(data_sources["protocol"])
                
            if "sap" in data_sources:
                self.data_handler.load_statistical_analysis_plan(data_sources["sap"])
                
            if "efficacy_data" in data_sources:
                self.data_handler.load_efficacy_data(data_sources["efficacy_data"])
                
            if "safety_data" in data_sources:
                self.data_handler.load_safety_data(data_sources["safety_data"])
                
            if "demographics" in data_sources:
                self.data_handler.load_demographics(data_sources["demographics"])
                
            if "tlf_directory" in data_sources:
                self.data_handler.load_tables_listings_figures(data_sources["tlf_directory"])
            
            # Validate the loaded data
            data_valid = self.data_handler.validate_all_data()
            
            if data_valid:
                logger.info("All study data loaded and validated successfully")
                
                # Initialize metrics tracker now that data is loaded
                self.metrics_tracker = MetricsTracker(self.document)
                
                # Initialize QC and approval managers
                self.qc_manager = QualityControlManager(self.document, self.data_handler.study_data)
                self.approval_manager = FinalApprovalManager(self.document)
                
                return True
            else:
                logger.error("Data validation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error loading study data: {str(e)}")
            return False
            
    def create_document_structure(self, section_titles: List[str]) -> None:
        """Create the initial document structure with empty sections.
        
        Args:
            section_titles: List of section titles to include in the document
        """
        logger.info("Creating document structure")
        
        for title in section_titles:
            section = CSRSection(title=title)
            self.document.add_section(section)
            
        logger.info(f"Created document structure with {len(section_titles)} sections")
        
    def generate_section(self, section_title: str, template: Optional[str] = None) -> bool:
        """Generate content for a specific section using AI.
        
        Args:
            section_title: The title of the section to generate
            template: Optional template guidance for the section
            
        Returns:
            bool: True if generation was successful, False otherwise
        """
        if section_title not in self.document.sections:
            logger.error(f"Section '{section_title}' not found in document")
            return False
            
        section = self.document.sections[section_title]
        
        # Update section status
        section.status = DocumentStatus.DRAFT_IN_PROGRESS
        self.document.update_status()
        
        # Organize the data needed for this section
        section_data = self.data_handler.organize_data_for_section(section_title)
        
        # Record data sources
        section.data_sources = list(section_data.keys())
        
        # Start timer for metrics
        start_time = time.time()
        
        try:
            # Generate content
            content = self.content_generator.generate_section_content(
                section_title, section_data, template
            )
            
            # Update section with generated content
            section.content = content
            section.ai_generated = True
            section.status = DocumentStatus.DRAFT_COMPLETED
            
            # Record generation metrics
            generation_time = time.time() - start_time
            if self.metrics_tracker:
                self.metrics_tracker.track_section_completion(
                    section_title, True, generation_time
                )
                
            logger.info(f"Successfully generated content for section '{section_title}'")
            self.document.update_status()
            return True
            
        except Exception as e:
            logger.error(f"Error generating content for section '{section_title}': {str(e)}")
            section.status = DocumentStatus.NOT_STARTED
            self.document.update_status()
            return False
            
    def generate_all_sections(self, templates: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """Generate content for all document sections.
        
        Args:
            templates: Optional dict mapping section titles to templates
            
        Returns:
            Dict mapping section titles to success status
        """
        results = {}
        
        for section_title in self.document.sections:
            template = templates.get(section_title) if templates else None
            success = self.generate_section(section_title, template)
            results[section_title] = success
            
        return results
        
    def submit_human_content(self, section_title: str, content: str, author_id: str) -> bool:
        """Submit human-written content for a section.
        
        Args:
            section_title: The title of the section
            content: The human-written content
            author_id: ID of the human author
            
        Returns:
            bool: True if submission was successful, False otherwise
        """
        if section_title not in self.document.sections:
            logger.error(f"Section '{section_title}' not found in document")
            return False
            
        section = self.document.sections[section_title]
        
        # Save old version in history if there was previous content
        if section.content:
            old_version = {
                "content": section.content,
                "status": section.status,
                "timestamp": datetime.datetime.now()
            }
            section.version_history.append(old_version)
            
        # Update with human content
        section.content = content
        section.ai_generated = False
        section.status = DocumentStatus.DRAFT_COMPLETED
        
        # Record author
        section.approval_status["author_id"] = author_id
        section.approval_status["authored_at"] = datetime.datetime.now()
        
        # Update document status
        self.document.update_status()
        
        logger.info(f"Human-written content submitted for section '{section_title}' by {author_id}")
        return True
        
    def process_review_feedback(self, section_title: str, reviewer_id: str, 
                               feedback: str, approved: bool) -> bool:
        """Process human review feedback on a section.
        
        Args:
            section_title: The title of the section
            reviewer_id: ID of the reviewer
            feedback: Review feedback
            approved: Whether the section is approved or needs revision
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Record review cycle metrics
            if self.metrics_tracker:
                # Calculate review cycle number
                if section_title in self.document.sections:
                    cycle_number = len(self.document.sections[section_title].review_comments) + 1
                else:
                    cycle_number = 1
                
                # Rough estimate of issues based on feedback length
                issues_count = feedback.count("\n") + 1 if feedback else 0
                
                # Track this review cycle
                review_time = 1.0  # Placeholder - in a real system would track actual time
                self.metrics_tracker.track_review_cycle(
                    section_title, cycle_number, review_time, issues_count
                )
            
            # Submit the feedback
            self.human_review_manager.submit_review_feedback(
                section_title, reviewer_id, feedback, approved
            )
            
            return True
        except Exception as e:
            logger.error(f"Error processing review feedback: {str(e)}")
            return False
            
    def process_qc_feedback(self, section_title: str, qc_reviewer_id: str,
                           feedback: str, approved: bool) -> bool:
        """Process QC feedback on a section.
        
        Args:
            section_title: The title of the section
            qc_reviewer_id: ID of the QC reviewer
            feedback: QC feedback
            approved: Whether the section passes QC
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Track QC metrics if needed
            
            # Submit the QC feedback
            self.qc_manager.submit_qc_feedback(
                section_title, qc_reviewer_id, feedback, approved
            )
            
            return True
        except Exception as e:
            logger.error(f"Error processing QC feedback: {str(e)}")
            return False
            
    def finalize_document(self) -> Optional[str]:
        """Finalize the document after all approvals.
        
        Returns:
            str: The final document content, or None if not approved
        """
        if self.document.status != DocumentStatus.APPROVED:
            # Check if we can initiate approval if not already done
            if self.document.status == DocumentStatus.QC_COMPLETED:
                self.approval_manager.initiate_approval_process()
            else:
                logger.warning(f"Cannot finalize document - not all sections approved. Current status: {self.document.status.value}")
                return None
        
        # Calculate time savings metrics before finalizing
        if self.metrics_tracker:
            # Example traditional writing time estimates in hours
            traditional_times = {title: 8.0 for title in self.document.sections}  # 8 hours per section
            self.metrics_tracker.calculate_time_savings(traditional_times)
        
        # Finalize the document
        final_content = self.approval_manager.finalize_document()
        
        # Generate final metrics report
        if self.metrics_tracker:
            metrics_report = self.metrics_tracker.generate_metrics_report()
            logger.info(f"Final metrics: {json.dumps(metrics_report, default=str)}")
            
        return final_content
        
    def get_document_status(self) -> Dict:
        """Get the current status of the document and all sections.
        
        Returns:
            Dict with document status information
        """
        section_statuses = {}
        for title, section in self.document.sections.items():
            section_statuses[title] = {
                "status": section.status.value,
                "ai_generated": section.ai_generated,
                "word_count": len(section.content.split()) if section.content else 0,
                "review_comments": len(section.review_comments),
                "qc_comments": len(section.qc_comments)
            }
            
        return {
            "title": self.document.title,
            "overall_status": self.document.status.value,
            "created_at": self.document.created_at,
            "last_modified": self.document.last_modified,
            "section_count": len(self.document.sections),
            "section_statuses": section_statuses
        }


# Example usage
def example_usage():
    """Example of how to use the CSR Drafting Agent."""
    # Initialize the agent
    agent = CSRDraftingAgent(
        title="Clinical Study Report - Trial XYZ-123", 
        api_key="YOUR_ANTHROPIC_API_KEY"
    )
    
    # Create document structure with ICH E3 sections
    agent.create_document_structure([
        "Title Page",
        "Synopsis",
        "Table of Contents",
        "Introduction",
        "Study Objectives",
        "Investigational Plan",
        "Study Population",
        "Efficacy Evaluation",
        "Safety Evaluation",
        "Discussion and Conclusions"
    ])
    
    # Load study data
    data_sources = {
        "protocol": "data/protocol.json",
        "sap": "data/sap.json",
        "efficacy_data": "data/efficacy.csv",
        "safety_data": "data/safety.csv",
        "demographics": "data/demographics.csv",
        "tlf_directory": "data/tlfs/"
    }
    agent.load_study_data(data_sources)
    
    # Generate content for all sections
    agent.generate_all_sections()
    
    # Assign sections for human review
    agent.human_review_manager.assign_section_for_review("Introduction", "reviewer001")
    agent.human_review_manager.assign_section_for_review("Study Objectives", "reviewer002")
    
    # Submit review feedback
    agent.process_review_feedback(
        "Introduction", 
        "reviewer001", 
        "Please add more context about the disease area and medical need.", 
        False  # Needs revision
    )
    
    # Submit positive review for another section
    agent.process_review_feedback(
        "Study Objectives", 
        "reviewer002", 
        "Objectives are clearly stated and align with the protocol.", 
        True  # Approved
    )
    
    # Assign for QC after review
    agent.qc_manager.assign_qc_review("Study Objectives", "qc001")
    
    # Submit QC feedback
    agent.process_qc_feedback(
        "Study Objectives", 
        "qc001", 
        "All regulatory requirements met. No issues found.", 
        True  # Passed QC
    )
    
    # Get document status
    status = agent.get_document_status()
    print(f"Document status: {status['overall_status']}")


if __name__ == "__main__":
    example_usage()
