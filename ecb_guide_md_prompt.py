import json
import re
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass, field, asdict
import os

@dataclass
class Requirement:
    index: str
    doc_name: str
    heading_1: str = ""
    heading_2: str = ""
    heading_3: str = ""
    heading_4: str = ""
    heading_5: str = ""
    heading_6: str = ""
    requirement_number: str = ""
    body_of_the_text: str = ""
    page_number: str = ""
    has_footnote: str = ""
    is_footnote: bool = False
    has_tables: bool = False
    has_formulas: bool = False
    has_figures: bool = False
    has_references: bool = False
    table_ids: List[str] = field(default_factory=list)
    formula_ids: List[str] = field(default_factory=list)
    figure_ids: List[str] = field(default_factory=list)
    reference_ids: List[str] = field(default_factory=list)

class MarkdownToJsonConverter:
    def __init__(self, markdown_text: str, doc_name: str = "document.pdf"):
        self.markdown_text = markdown_text
        self.doc_name = doc_name
        self.requirements: List[Requirement] = []
        self.current_headings = {"h1": "", "h2": "", "h3": "", "h4": "", "h5": "", "h6": ""}
        self.current_page = "1"
        self.requirement_counter = 0
        self.footnote_index = {}  # Store footnote number -> content mapping
        
    def parse(self) -> Dict[str, List[Dict]]:
        # First pass: build footnote index
        self._build_footnote_index()
        
        lines = self.markdown_text.split('\n')
        i = 0
        current_content = []
        current_req_number = ""
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip footnote definitions as they're already indexed
            if line.startswith('<footnote>'):
                i += 1
                continue
            
            if line.startswith('<page>') and line.endswith('</page>'):
                self.current_page = re.search(r'<page>(\d+)</page>', line).group(1)
                i += 1
                continue
            
            if line.startswith('#'):
                if current_content:
                    self._process_paragraph(current_content, current_req_number)
                    current_content = []
                    current_req_number = ""
                self._process_heading(line)
                i += 1
                continue
            
            req_match = re.match(r'^(\d+)\.\s+(.+)', line)
            if req_match:
                if current_content:
                    self._process_paragraph(current_content, current_req_number)
                    current_content = []
                current_req_number = req_match.group(1)
                current_content.append(req_match.group(2))
                i += 1
                continue
            
            if line or current_content:
                if line.startswith('<table>'):
                    table_content = ['<table>']
                    i += 1
                    while i < len(lines) and not lines[i].strip().endswith('</table>'):
                        table_content.append(lines[i])
                        i += 1
                    if i < len(lines):
                        table_content.append(lines[i])
                    current_content.extend(table_content)
                    i += 1
                    continue
                
                if line.startswith('<figure>'):
                    figure_content = ['<figure>']
                    i += 1
                    while i < len(lines) and not lines[i].strip().endswith('</figure>'):
                        figure_content.append(lines[i])
                        i += 1
                    if i < len(lines):
                        figure_content.append(lines[i])
                    current_content.extend(figure_content)
                    i += 1
                    continue
                
                if line.startswith('<formula>'):
                    formula_content = ['<formula>']
                    i += 1
                    while i < len(lines) and not lines[i].strip().endswith('</formula>'):
                        formula_content.append(lines[i])
                        i += 1
                    if i < len(lines):
                        formula_content.append(lines[i])
                    current_content.extend(formula_content)
                    i += 1
                    continue
                
                if line or (current_content and i + 1 < len(lines)):
                    current_content.append(line)
            
            i += 1
        
        if current_content:
            self._process_paragraph(current_content, current_req_number)
        
        return {"requirements": [asdict(req) for req in self.requirements]}
    
    def _build_footnote_index(self):
        """Build an index of all footnotes in the document"""
        footnote_pattern = r'<footnote>\[Footnote (\d+)\]: ([^<]+)</footnote>'
        footnote_matches = re.findall(footnote_pattern, self.markdown_text)
        for num, content in footnote_matches:
            self.footnote_index[num] = content
    
    def _process_heading(self, line: str):
        level = len(re.match(r'^(#+)', line).group(1))
        heading_text = line.lstrip('#').strip()
        for i in range(1, 7):
            if i == level:
                self.current_headings[f"h{i}"] = heading_text
            elif i > level:
                self.current_headings[f"h{i}"] = ""
    
    def _process_paragraph(self, paragraph_lines: List[str], req_number: str = ""):
        if not paragraph_lines:
            return
        
        # Join paragraph lines (without footnotes which are already indexed)
        clean_lines = [line for line in paragraph_lines if not line.startswith('<footnote>')]
        full_text = '\n'.join(clean_lines)
        
        # Find footnote references in the text - ONLY superscripts
        footnote_numbers = []
        
        # Check for superscript footnote references (¹²³ etc)
        superscript_refs = re.findall(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+', full_text)
        for ref in superscript_refs:
            # Convert superscript to regular number
            num = ref.replace('¹', '1').replace('²', '2').replace('³', '3').replace('⁴', '4').replace('⁵', '5').replace('⁶', '6').replace('⁷', '7').replace('⁸', '8').replace('⁹', '9').replace('⁰', '0')
            if num not in footnote_numbers:
                footnote_numbers.append(num)
        
        # Append footnotes directly after the paragraph text
        if footnote_numbers:
            footnote_text = []
            for num in footnote_numbers:
                if num in self.footnote_index:
                    footnote_text.append(f"\n<footnote>[Footnote {num}]: {self.footnote_index[num]}</footnote>")
            if footnote_text:
                full_text += ''.join(footnote_text)
        
        # Check for elements
        has_tables = '<table>' in full_text
        has_figures = '<figure>' in full_text
        has_formulas = '<formula>' in full_text
        
        # Extract IDs
        table_ids = []
        figure_ids = []
        formula_ids = []
        
        if has_tables:
            table_count = full_text.count('<table>')
            table_ids = [f"table_{self.requirement_counter}_{i+1}" for i in range(table_count)]
        
        if has_figures:
            figure_count = full_text.count('<figure>')
            figure_ids = [f"figure_{self.requirement_counter}_{i+1}" for i in range(figure_count)]
        
        if has_formulas:
            formula_count = full_text.count('<formula>')
            formula_ids = [f"formula_{self.requirement_counter}_{i+1}" for i in range(formula_count)]
        
        # Extract references
        references = self._extract_references(full_text)
        
        self.requirement_counter += 1
        index = f"{self.doc_name.replace('.pdf', '')}_{self.current_page}_{self.requirement_counter:04d}"
        
        req = Requirement(
            index=index,
            doc_name=self.doc_name,
            heading_1=self.current_headings["h1"],
            heading_2=self.current_headings["h2"],
            heading_3=self.current_headings["h3"],
            heading_4=self.current_headings["h4"],
            heading_5=self.current_headings["h5"],
            heading_6=self.current_headings["h6"],
            requirement_number=req_number,
            body_of_the_text=full_text,
            page_number=self.current_page,
            has_footnote=",".join(footnote_numbers) if footnote_numbers else "",
            is_footnote=bool(footnote_numbers),
            has_tables=has_tables,
            has_formulas=has_formulas,
            has_figures=has_figures,
            has_references=bool(references),
            table_ids=table_ids,
            formula_ids=formula_ids,
            figure_ids=figure_ids,
            reference_ids=references
        )
        
        self.requirements.append(req)
    
    def _extract_references(self, text: str) -> List[str]:
        references = []
        patterns = [
            r'Regulation \(EU\) No \d+/\d+',
            r'Directive \d+/\d+/\w+',
            r'Commission Delegated Regulation \(EU\) No \d+/\d+',
            r'Article \d+(?:\(\d+\))?(?:\([a-z]\))?',
            r'CRR\d?',
            r'CRD\d?',
            r'GDPR',
            r'Basel [IVX]+',
            r'EBA/\w+/\d+/\d+',
            r'ECB Guide [^,\.]+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            references.extend(matches)
        
        seen = set()
        unique_refs = []
        for ref in references:
            if ref not in seen:
                seen.add(ref)
                unique_refs.append(ref)
        
        return unique_refs

def process_markdown(markdown_file_path: str, doc_name: str = None) -> pd.DataFrame:
    if doc_name is None:
        doc_name = os.path.basename(markdown_file_path).replace('.md', '.pdf')
    
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    
    converter = MarkdownToJsonConverter(markdown_text, doc_name)
    result = converter.parse()
    
    df = pd.DataFrame(result['requirements'])
    
    list_columns = ['table_ids', 'formula_ids', 'figure_ids', 'reference_ids']
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ', '.join(x) if x else '')
    
    json_output_path = markdown_file_path.replace('.md', '_output.json')
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    csv_output_path = markdown_file_path.replace('.md', '_output.csv')
    df.to_csv(csv_output_path, index=False, encoding='utf-8')
    
    return df


df = process_markdown('ecb_guide.md')
df
