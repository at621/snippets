import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging

# Check if tiktoken is available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not installed. Token count will use character-based estimation.")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EURLexParser:
    """Simplified EUR-Lex document parser that correctly handles all numbering"""
    
    # Define hierarchy levels in order
    HIERARCHY_LEVELS = ['part', 'title', 'chapter', 'section', 'subsection']
    
    def __init__(self):
        # Initialize hierarchy with both number and heading for each level
        self.hierarchy = {f'{level}{"_heading" if is_heading else ""}': '' 
                         for level in self.HIERARCHY_LEVELS 
                         for is_heading in [False, True]}
        self.articles = []
        self.pending_division = None
        
        # Initialize tiktoken encoder if available
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except:
                self.encoding = None
        else:
            self.encoding = None
    
    def clean_text(self, text):
        """Clean text by removing modification markers and extra whitespace"""
        if not text:
            return ""
        
        # Remove modification markers and normalize whitespace
        text = re.sub(r'►[A-Z]\d+|◄|▼[A-Z]\d+|▲', '', text)
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(?<!\d)\s+\.', '.', text)
        
        return text.strip()
    
    def reset_hierarchy_below(self, level):
        """Reset all hierarchy levels below the given level"""
        levels = self.HIERARCHY_LEVELS
        start_idx = levels.index(level) + 1 if level in levels else 0
        
        for lvl in levels[start_idx:]:
            self.hierarchy[lvl] = ''
            self.hierarchy[f'{lvl}_heading'] = ''
    
    def update_hierarchy(self, text1, text2=None):
        """Update hierarchy based on division text"""
        text1_upper = text1.upper()
        
        # Determine the hierarchy level
        for level in self.HIERARCHY_LEVELS:
            if level.upper() in text1_upper and (
                text1.strip().upper().startswith(level.upper()) or 
                f' {level.upper()} ' in f' {text1_upper} '
            ):
                # Special handling for PART with inline heading
                if level == 'part' and not text2:
                    match = re.match(r'^(PART\s+[A-Z]+)\s*[-\u2013\u2014]\s*(.+)$', text1, re.IGNORECASE)
                    if match:
                        self.hierarchy[level] = match.group(1).strip()
                        self.hierarchy[f'{level}_heading'] = match.group(2).strip()
                    else:
                        self.hierarchy[level] = text1
                        self.hierarchy[f'{level}_heading'] = ''
                else:
                    self.hierarchy[level] = text1
                    self.hierarchy[f'{level}_heading'] = text2 or ''
                
                self.reset_hierarchy_below(level)
                logging.info(f"Found {level.capitalize()}: {text1} - {text2 or ''}")
                return True
        return False
    
    def extract_grid_list(self, grid_container):
        """Extract content from grid-container preserving all numbering"""
        items = []
        
        # Process pairs of grid columns
        column1_divs = grid_container.find_all('div', 
            class_=lambda c: c and 'grid-list-column-1' in c, recursive=False)
        
        for col1_div in column1_divs:
            marker = col1_div.get_text(strip=True)
            
            # Find corresponding column-2
            col2_div = col1_div.find_next_sibling(
                'div', class_=lambda c: c and 'grid-list-column-2' in c)
            
            if col2_div:
                content_parts = []
                
                # Process all children of column 2
                for child in col2_div.children:
                    if hasattr(child, 'name'):
                        if child.name == 'div' and 'grid-container' in ' '.join(child.get('class', [])):
                            # Nested grid list
                            nested_content = self.extract_grid_list(child)
                            if nested_content:
                                content_parts.append(nested_content)
                        else:
                            # Other elements
                            text = self.clean_text(child.get_text())
                            if text:
                                content_parts.append(text)
                    else:
                        # Text node
                        text = str(child).strip()
                        if text:
                            content_parts.append(text)
                
                content = ' '.join(content_parts)
                if marker and content:
                    items.append(f"{marker} {content}")
        
        return ' '.join(items)
    
    def extract_article_content(self, article_div):
        """Extract complete article content preserving all numbering"""
        # Get article title
        title_elem = article_div.find('p', class_='title-article-norm')
        if not title_elem:
            return None
        
        article_heading = self.clean_text(title_elem.get_text())
        
        # Extract article number
        match = re.match(r'Article\s+(\d+[a-zA-Z]*)', article_heading, re.IGNORECASE)
        if not match:
            return None
        article_number = match.group(1)
        
        # Get subtitle if exists
        subtitle_elem = article_div.find('p', class_='stitle-article-norm')
        if subtitle_elem:
            subtitle = self.clean_text(subtitle_elem.get_text())
            if subtitle:
                article_heading += f" - {subtitle}"
        
        # Extract all content parts
        content_parts = []
        
        # Process all direct children that are norm elements
        for child in article_div.children:
            if not hasattr(child, 'name'):
                continue
            
            # Skip elements we don't want
            if (child.name == 'p' and 
                any(cls in child.get('class', []) for cls in 
                    ['modref', 'title-article-norm', 'stitle-article-norm'])):
                continue
            
            # Process norm paragraphs
            if child.name == 'p' and 'norm' in child.get('class', []):
                text = self.clean_text(child.get_text())
                if text:
                    content_parts.append(text)
            
            # Process grid containers
            elif child.name == 'div' and 'grid-container' in ' '.join(child.get('class', [])):
                grid_content = self.extract_grid_list(child)
                if grid_content:
                    content_parts.append(grid_content)
            
            # Process div.norm elements
            elif child.name == 'div' and 'norm' in child.get('class', []):
                # Get paragraph number if exists
                para_span = child.find('span', class_='no-parag')
                para_num = para_span.get_text(strip=True) if para_span else ""
                
                # Extract content
                text_parts = []
                for elem in child.children:
                    if hasattr(elem, 'name'):
                        if elem.name == 'span' and 'no-parag' in elem.get('class', []):
                            continue
                        elif elem.name == 'div' and 'grid-container' in ' '.join(elem.get('class', [])):
                            grid_content = self.extract_grid_list(elem)
                            if grid_content:
                                text_parts.append(grid_content)
                        else:
                            text = self.clean_text(elem.get_text())
                            if text:
                                text_parts.append(text)
                    else:
                        text = str(elem).strip()
                        if text:
                            text_parts.append(text)
                
                combined_text = ' '.join(text_parts)
                if combined_text:
                    content_parts.append(f"{para_num} {combined_text}" if para_num else combined_text)
        
        return {
            'article_number': article_number,
            'article_heading': article_heading,
            'text': ' '.join(content_parts),
            **self.hierarchy  # Add current hierarchy
        }
    
    def parse_document(self, url):
        """Parse EUR-Lex document from URL"""
        logging.info(f"Fetching document from: {url}")
        
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all relevant elements
        all_elements = soup.find_all(['div', 'p'], class_=True)
        
        for element in all_elements:
            classes = ' '.join(element.get('class', []))
            text = self.clean_text(element.get_text())
            
            if not text:
                continue
            
            # Handle title-division pairs
            if 'title-division-1' in classes:
                self.pending_division = text
            elif 'title-division-2' in classes and self.pending_division:
                self.update_hierarchy(self.pending_division, text)
                self.pending_division = None
            
            # Handle other section types
            elif any(cls in classes for cls in ['ti-section-1', 'sti-section-1']):
                self.update_hierarchy(text)
            
            # Process articles
            elif 'eli-subdivision' in classes and element.name == 'div':
                article_data = self.extract_article_content(element)
                if article_data:
                    self.articles.append(article_data)
                    logging.info(f"Processed Article {article_data['article_number']}")
        
        return self.create_dataframe()
    
    def create_dataframe(self):
        """Create and enhance the final DataFrame"""
        if not self.articles:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.articles)
        
        # Rename columns for consistency
        df.rename(columns={
            'article_number': 'Article_Number',
            'article_heading': 'Article_Heading',
            'text': 'Text'
        }, inplace=True)
        
        # Add validation columns
        if self.encoding:
            df['Token_Count'] = df['Text'].apply(lambda x: len(self.encoding.encode(x)) if x else 0)
        else:
            df['Token_Count'] = df['Text'].apply(lambda x: len(x) // 4 if x else 0)
        
        df['Ends_With_Dot'] = df['Text'].apply(lambda x: x.strip().endswith('.') if x else False)
        df['Text_With_Pagebreaks'] = df['Text'].apply(self.add_pagebreaks_to_text)
        
        # Capitalize hierarchy column names
        for col in df.columns:
            if col not in ['Article_Number', 'Article_Heading', 'Text', 'Token_Count', 'Ends_With_Dot', 'Text_With_Pagebreaks']:
                new_name = col.replace('_', ' ').title().replace(' ', '_')
                df.rename(columns={col: new_name}, inplace=True)
        
        # Remove empty hierarchy columns
        hierarchy_cols = [col for col in df.columns if col not in 
                         ['Article_Number', 'Article_Heading', 'Text', 'Token_Count', 'Ends_With_Dot', 'Text_With_Pagebreaks']]
        
        for col in hierarchy_cols:
            if df[col].str.strip().eq('').all():
                df.drop(columns=[col], inplace=True)
        
        # Reorder columns: hierarchy → validation → article info → text with pagebreaks
        hierarchy_cols = [col for col in df.columns if col not in 
                         ['Article_Number', 'Article_Heading', 'Text', 'Token_Count', 'Ends_With_Dot', 'Text_With_Pagebreaks']]
        
        hierarchy_number_cols = [col for col in hierarchy_cols if not col.endswith('_Heading')]
        hierarchy_heading_cols = [col for col in hierarchy_cols if col.endswith('_Heading')]
        
        new_order = (hierarchy_number_cols + hierarchy_heading_cols + 
                    ['Token_Count', 'Ends_With_Dot', 'Article_Number', 'Article_Heading', 'Text', 'Text_With_Pagebreaks'])
        
        return df[new_order]
    
    def add_pagebreaks_to_text(self, text):
        """Add pagebreaks before subheadings"""
        if not text:
            return text
        
        # Apply patterns for different numbering types
        patterns = [
            (r'(?<=[.;,\s])(\s*)(\([ivxlcdm]+\))', r'\n\n\2'),  # (i), (ii), etc.
            (r'(?<=[.;,\s])(\s*)(\([a-z]\))', r'\n\n\2'),       # (a), (b), etc.
            (r'(?<=[.;,\s])(\s*)(\(\d+\))', r'\n\n\2'),         # (1), (2), etc.
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return re.sub(r'\n{3,}', '\n\n', text).strip()


def parse_eurlex_document(url, output_file='eurlex_parsed.csv', save_csv=True):
    """Parse EUR-Lex document from URL"""
    parser = EURLexParser()
    
    try:
        df = parser.parse_document(url)
        
        print(f"\nParsing completed! Total articles found: {len(df)}")
        
        if not df.empty:
            if save_csv:
                # Save to CSV (excluding Text_With_Pagebreaks)
                save_columns = [col for col in df.columns if col != 'Text_With_Pagebreaks']
                df[save_columns].to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"Saved to: {output_file}")
            
            # Print summary
            print_summary(df)
            
            return df
        else:
            print("No articles found in the document.")
            return df
            
    except Exception as e:
        print(f"Error parsing document: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def print_summary(df):
    """Print a concise summary of the parsed data"""
    print("\n" + "="*60)
    print("DOCUMENT STRUCTURE SUMMARY")
    print("="*60)
    
    # Document hierarchy
    hierarchy_cols = [col for col in df.columns if col not in 
                     ['Article_Number', 'Article_Heading', 'Text', 'Token_Count', 'Ends_With_Dot', 'Text_With_Pagebreaks']]
    
    if hierarchy_cols:
        print("\nDocument hierarchy:")
        for base in ['Part', 'Title', 'Chapter', 'Section', 'Subsection']:
            if base in df.columns:
                count = df[base].nunique()
                if count > 0:
                    has_heading = f"{base}_Heading" in df.columns
                    print(f"  - {base}: {count} unique {'(with headings)' if has_heading else ''}")
    
    # Validation summary
    print(f"\nValidation summary:")
    print(f"  - Total tokens: {df['Token_Count'].sum():,}")
    print(f"  - Average tokens per article: {df['Token_Count'].mean():.0f}")
    print(f"  - Articles ending with period: {df['Ends_With_Dot'].sum()}/{len(df)}")
    
    # Sample articles
    print(f"\nFirst 5 articles:")
    print(df[['Article_Number', 'Article_Heading', 'Token_Count']].head())
    
    # Numbering patterns
    print("\nNumbering patterns found:")
    for pattern, desc in [(r'\(\d+\)', '(1), (2), (3)'), 
                         (r'\([a-z]\)', '(a), (b), (c)')]:
        count = df['Text'].apply(lambda x: bool(re.search(pattern, x))).sum()
        print(f"  - Articles with {desc}: {count}")


def check_article(df, article_number):
    """Check a specific article for content and numbering"""
    article = df[df['Article_Number'] == str(article_number)]
    if article.empty:
        print(f"Article {article_number} not found")
        return
    
    row = article.iloc[0]
    print(f"\nArticle {article_number}: {row['Article_Heading']}")
    print(f"Tokens: {row['Token_Count']}, Ends with dot: {row['Ends_With_Dot']}")
    
    # Check numbering patterns
    text = row['Text']
    patterns = {
        'Main (1), (2)': re.findall(r'\(\d+\)', text),
        'Letters (a), (b)': re.findall(r'\([a-z]\)', text),
        'Roman (i), (ii)': re.findall(r'\([ivxlcdm]+\)', text, re.IGNORECASE)
    }
    
    print("\nNumbering found:")
    for desc, matches in patterns.items():
        if matches:
            print(f"  {desc}: {', '.join(matches[:5])}{' ...' if len(matches) > 5 else ''}")
    
    print(f"\nText preview:")
    print("-" * 60)
    print(text[:500] + "..." if len(text) > 500 else text)


# Usage example:

url = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02013R0575-20250101"
df = parse_eurlex_document(url)

# Quick checks
if not df.empty:
    print(f"\n✅ Successfully parsed {len(df)} articles")
    check_article(df, '5a')
    check_article(df, '10')
