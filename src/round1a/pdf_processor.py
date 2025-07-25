import pdfplumber
import json
import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Heading:
    level: str
    text: str
    page: int

class PDFProcessor:
    def __init__(self):
        self.title = ""
        self.headings: List[Heading] = []
    
    def _is_heading(self, text: str, font_name: Optional[str], font_size: Optional[float]) -> bool:
        """Determine if text is likely a heading based on characteristics"""
        if not text:
            return False
        
        text = text.strip()
        if len(text) < 2 or len(text) > 100:
            return False
        
        # Check for common heading patterns
        if (text.isupper() or 
            text.istitle() or 
            re.match(r'^(Chapter|Section|Part)\s+[IVXLCDM0-9]+', text, re.IGNORECASE)):
            return True
        
        return False
    
    def _determine_heading_level(self, font_size: float, previous_level: Optional[str]) -> str:
        """Determine heading level based on font size and context"""
        if font_size > 16:
            return "H1"
        elif font_size > 14:
            return "H2" if previous_level != "H1" else "H2"
        elif font_size > 12:
            return "H3" if previous_level in ["H1", "H2"] else "H3"
        else:
            return "H3"
    
    def _extract_title(self, first_page_text: str) -> str:
        """Attempt to extract title from first page"""
        lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
        if lines:
            # First non-empty line is often the title
            return lines[0]
        return os.path.basename(self.filepath).replace('.pdf', '')
    
    def process_pdf(self, filepath: str) -> Dict:
        """Process a PDF file and extract its structure"""
        self.filepath = filepath
        self.headings = []
        
        with pdfplumber.open(filepath) as pdf:
            previous_level = None
            
            # Extract title from first page
            first_page = pdf.pages[0]
            first_page_text = first_page.extract_text()
            self.title = self._extract_title(first_page_text)
            
            for page_num, page in enumerate(pdf.pages, start=1):
                words = page.extract_words(
                    x_tolerance=1,
                    y_tolerance=1,
                    keep_blank_chars=False,
                    use_text_flow=True,
                    extra_attrs=["fontname", "size"]
                )
                
                # Group words by line
                lines = {}
                for word in words:
                    y = round(word['top'])
                    if y not in lines:
                        lines[y] = []
                    lines[y].append(word)
                
                # Process each line
                for y_pos in sorted(lines.keys()):
                    line_words = lines[y_pos]
                    text = ' '.join([w['text'] for w in line_words])
                    font_name = line_words[0]['fontname'] if line_words else None
                    font_size = line_words[0]['size'] if line_words else None
                    
                    if self._is_heading(text, font_name, font_size):
                        level = self._determine_heading_level(font_size, previous_level)
                        self.headings.append(Heading(level=level, text=text, page=page_num))
                        previous_level = level
        
        return self._generate_output()
    
    def _generate_output(self) -> Dict:
        """Generate the output JSON structure"""
        return {
            "title": self.title,
            "outline": [
                {"level": h.level, "text": h.text, "page": h.page}
                for h in self.headings
            ]
        }