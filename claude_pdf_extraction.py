#!/usr/bin/env python3
"""
Extract regulatory requirements from PDF to structured JSON using Claude API.
"""

import anthropic
import base64
import json
import sys
import os
import time

# CONFIGURATION
API_KEY = os.environ.get("CLAUDE_KEY")  # Get API key from environment variable
PDF_FILE = "Guidelines on PD and LGD estimation (EBA-GL-2017-16)_EN.pdf"    # Replace with your PDF file path
OUTPUT_FILE = "extracted_requirements.json"  # Output JSON file name

# Check if API key is set
if not API_KEY:
    print("Error: CLAUDE_KEY environment variable is not set")
    print("Set it with: export CLAUDE_KEY='your-api-key-here'")
    sys.exit(1)

# Full extraction prompt
PROMPT = """# Regulatory Document PDF to JSON Extraction Guide
 
## Task Overview
Extract regulatory requirements from PDF documents into structured JSON format, preserving all content, formatting, and references while following specific organizational rules.
 
## Core Extraction Principles
 
### Document Structure
- **heading_1**: Document title from page 1 (join multi-line titles with spaces, remains constant throughout)
- **heading_2-6**: Hierarchical section structure
  - Parent headings persist when child headings change
  - Patterns: `1,2,3...` = major sections; `1.1,1.2...` = subsections; `PART/CHAPTER/ARTICLE` = logical divisions
  - Use empty string `""` for unused heading levels
 
### Critical Rules
1. **Extract only paragraph content** - never standalone headings
2. **Skip entirely** any sections titled "Definitions", "Glossary", "Terms and Definitions", "Abbreviations"
3. **Always use actual page numbers** from the document (e.g., 46, 47, 48), not sequential snippet numbering
4. **Preserve exact text** using Python markdown for special characters and formatting
 
## Paragraph Handling
 
### Basic Paragraph Rules
- Each paragraph = one JSON entry
- Merge paragraphs with their introduced lists (when ending with ":" or "the following")
- Join list items with newlines
- Fix obvious hyphenated line breaks
 
### Page Break Continuation
**Indicators of continued paragraphs across pages:**
- Uncapitalized starting letter (unless proper noun/acronym)
- Previous page ends mid-sentence (no period/question mark/exclamation)
- Previous page ends with comma/semicolon/connecting words (and, or, but)
- Continuing list or enumeration
- Incomplete sentence structure
 
**When merging:**
- Join with single space
- Use comma-separated page numbers (e.g., "46,47")
- Rejoin hyphenated words split across pages
 
## Special Content Integration
 
### Tables
Append to the preceding paragraph's `body_of_the_text`:
```
<br><br>
<table>
[Table X: Full title] 1-3 sentence summary capturing essential information.
</table>
```
- Set `has_tables: true`
- Add to `table_ids` array
 
### Figures
Append to the preceding paragraph's `body_of_the_text`:
```
<br><br>
<figure>
[Figure X: Full title] 1-3 sentence summary of key information.
</figure>
```
- Set `has_figures: true`
- Add to `figure_ids` array
 
### Formulas
Append to the preceding paragraph's `body_of_the_text`:
```
<br><br>
<formula>
[Equation X] Mathematical notation in markdown. Brief explanation of what it calculates.
</formula>
```
- Set `has_formulas: true`
- Add to `formula_ids` array
 
### Footnotes
Keep superscript reference in main text and append:
```
<br><br>
<footnote>
[Footnote 1] Exact footnote text.
</footnote>
```
- Update `has_footnote` with comma-separated numbers (e.g., "1,2,3")
- Set `is_footnote: true` when content is embedded
 
## Indexing System
 
### Index Format
`[doc_name_without_extension]_[page_number]_[paragraph_position]_[sequence_number]`
 
Example: `regulation_2024_46_3_0001`
- doc_name_without_extension: filename without extension
- page_number: ACTUAL page number from document
- paragraph_position: continuous count across entire snippet
- sequence_number: 4-digit sequential (0001, 0002, etc.)
 
## Content Analysis Fields
 
### Boolean Flags
- `has_tables`: Contains tables (including appended)
- `has_formulas`: Contains mathematical formulas/equations
- `has_figures`: Contains images/figures/diagrams
- `has_references`: References other articles/sections
- `is_footnote`: Footnote content is embedded in body_of_the_text
 
### Identifier Arrays
- `table_ids`: ["Table_1.1", "Table_1.2"]
- `formula_ids`: ["Eq_1", "Formula_3"]
- `figure_ids`: ["Fig_1", "Fig_2"]
- `reference_ids`: ["Article 502 of Regulation (EU) No 575/2013"]
 
### Special Fields
- `has_footnote`: Comma-separated footnote numbers or empty string
- `requirement_number`: List markers like (1), 1), 1. if present
- `page_number`: Actual page numbers (e.g., "46" or "46,47" if spans pages)
 
## Text Preservation
 
### Use Python Markdown for:
- Superscripts: `x²` or `10^6`
- Subscripts: `H₂O` or `x_i`
- Greek letters: `α, β, Σ, Δ`
- Mathematical symbols: `≤, ≥, ±, ∞, √`
- Special characters: `€, °C, §, ©`
 
## Output JSON Structure
 
```json
{
  "requirements": [
    {
      "index": "filename_46_1_0001",
      "doc_name": "filename.pdf",
      "heading_1": "Document Title",
      "heading_2": "Section Name",
      "heading_3": "",
      "heading_4": "",
      "heading_5": "",
      "heading_6": "",
      "requirement_number": "(1)",
      "body_of_the_text": "Paragraph text with footnote¹ reference.\n\n<br><br>\n<footnote>\n[Footnote 1] This applies when temperature ≥ 25°C.\n</footnote>\n\n<br><br>\n<formula>\n[Equation 1] Δ = b² - 4ac. This calculates the discriminant.\n</formula>\n\n<br><br>\n<table>\n[Table 1: Risk Categories] Summary of five risk weight categories from 0% to 150%.\n</table>",
      "page_number": "46,47",
      "has_footnote": "1",
      "is_footnote": true,
      "has_tables": true,
      "has_formulas": true,
      "has_figures": false,
      "has_references": false,
      "table_ids": ["Table_1"],
      "formula_ids": ["Eq_1"],
      "figure_ids": [],
      "reference_ids": []
    }
  ]
}
```
 
## Processing Checklist
 
1. ✓ Identify actual page numbers from document
2. ✓ Track heading hierarchy throughout
3. ✓ Skip definition/glossary sections
4. ✓ Check for paragraph continuation across pages
5. ✓ Append tables/figures/formulas/footnotes to preceding paragraphs
6. ✓ Preserve all special characters using markdown
7. ✓ Extract and categorize all references
8. ✓ Generate unique index for each entry
9. ✓ Set all boolean flags and populate ID arrays
10. ✓ Validate JSON structure before output

IMPORTANT: Return ONLY the JSON output, no additional text or explanation."""

# Initialize Claude client
try:
    client = anthropic.Anthropic(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing API client: {e}")
    sys.exit(1)

# Read and encode PDF
try:
    print(f"Reading PDF: {PDF_FILE}")
    with open(PDF_FILE, 'rb') as f:
        pdf_bytes = f.read()
        pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
        print(f"PDF size: {pdf_size_mb:.2f} MB")
        pdf_data = base64.b64encode(pdf_bytes).decode('utf-8')
except FileNotFoundError:
    print(f"Error: PDF file '{PDF_FILE}' not found")
    sys.exit(1)
except Exception as e:
    print(f"Error reading PDF: {e}")
    sys.exit(1)

# Send to Claude API
print("Sending to Claude API for structured extraction...")
start_time = time.time()

try:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,  # Increased for JSON output
        temperature=0,     # Deterministic for structured extraction
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": PROMPT
                    }
                ]
            }
        ]
    )
    
    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Get token usage
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    total_tokens = input_tokens + output_tokens
    
    # Get response text
    response_text = response.content[0].text
    
    # Try to parse as JSON to validate
    try:
        json_data = json.loads(response_text)
        
        # Save to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Extraction complete! Saved to: {OUTPUT_FILE}")
        print(f"✓ Extracted {len(json_data['requirements'])} requirements")
        print(f"✓ Processing time: {processing_time:.2f} seconds")
        print(f"\n📊 Token Usage:")
        print(f"   • Input tokens: {input_tokens:,}")
        print(f"   • Output tokens: {output_tokens:,}")
        print(f"   • Total tokens: {total_tokens:,}")
        
    except json.JSONDecodeError as e:
        print(f"\nWarning: Response is not valid JSON. Saving raw response...")
        error_output_file = OUTPUT_FILE.replace('.json', '_response.txt')
        with open(error_output_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"Raw response saved to: {error_output_file}")
        print(f"JSON Error: {e}")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"\n📊 Token Usage:")
        print(f"   • Input tokens: {input_tokens:,}")
        print(f"   • Output tokens: {output_tokens:,}")
        print(f"   • Total tokens: {total_tokens:,}")
        
except Exception as e:
    print(f"Error calling API: {e}")
    sys.exit(1)
