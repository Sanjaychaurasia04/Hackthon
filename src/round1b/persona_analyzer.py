import os
import json
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .utils import load_pdf_text, chunk_text
from src.round1a.pdf_processor import PDFProcessor

@dataclass
class RelevantSection:
    document: str
    page: int
    section_title: str
    content: str
    importance_rank: float

class PersonaAnalyzer:
    def __init__(self):
        # Use a small sentence transformer model that fits within 1GB constraint
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pdf_processor = PDFProcessor()
    
    def load_persona(self, persona_file: str) -> Dict:
        """Load persona definition from JSON file"""
        with open(persona_file, 'r') as f:
            return json.load(f)
    
    def load_job_description(self, job_file: str) -> Dict:
        """Load job-to-be-done from JSON file"""
        with open(job_file, 'r') as f:
            return json.load(f)
    
    def analyze_documents(self, document_paths: List[str], persona: Dict, job: Dict) -> Dict:
        """Analyze documents based on persona and job requirements"""
        # Embed the job description
        job_embedding = self.model.encode(job['description'])
        
        sections = []
        
        for doc_path in document_paths:
            # Get document structure
            doc_structure = self.pdf_processor.process_pdf(doc_path)
            
            # Load full text
            full_text = load_pdf_text(doc_path)
            
            # Process each section
            for heading in doc_structure['outline']:
                # Get section content (simplified - would need better text extraction)
                section_content = self._extract_section_content(full_text, heading)
                
                # Embed section content
                section_embedding = self.model.encode(section_content)
                
                # Calculate similarity to job description
                similarity = cosine_similarity(
                    [job_embedding],
                    [section_embedding]
                )[0][0]
                
                sections.append(RelevantSection(
                    document=os.path.basename(doc_path),
                    page=heading['page'],
                    section_title=heading['text'],
                    content=section_content,
                    importance_rank=float(similarity)
                ))
        
        # Sort sections by importance
        sections.sort(key=lambda x: x.importance_rank, reverse=True)
        
        return self._generate_output(document_paths, persona, job, sections)
    
    def _extract_section_content(self, full_text: str, heading: Dict) -> str:
        """Extract content for a section (simplified implementation)"""
        # This is a simplified implementation - would need better text extraction
        # based on PDF structure in a real implementation
        return f"{heading['text']}: " + full_text[:500]  # Just a placeholder
    
    def _generate_output(self, document_paths: List[str], persona: Dict, 
                        job: Dict, sections: List[RelevantSection]) -> Dict:
        """Generate the output JSON structure"""
        return {
            "metadata": {
                "input_documents": [os.path.basename(p) for p in document_paths],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section.document,
                    "page_number": section.page,
                    "section_title": section.section_title,
                    "importance_rank": section.importance_rank
                }
                for section in sections
            ],
            "sub_section_analysis": [
                {
                    "document": section.document,
                    "page_number": section.page,
                    "refined_text": section.content[:500],  # Limit length for demo
                    "relevance_score": section.importance_rank
                }
                for section in sections[:5]  # Just top 5 for demo
            ]
        }