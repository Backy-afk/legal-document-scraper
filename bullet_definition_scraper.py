import fitz  # PyMuPDF
import re
import csv
import os

# SETTINGS
pdf_folder = r"C:\Users\bella\Downloads\compressed"      # Folder containing all your PDFs
output_csv = "bullet_point_definitions.csv"

def clean_text(text):
    """Clean text but preserve structure"""
    if not text:
        return ""
    # Remove weird bullets but keep structure
    text = re.sub(r'[•▪▫◦‣⁃]', '•', text)  # Normalize bullets
    text = ' '.join(text.split())
    return text.strip()

def extract_bullet_point_definitions(text, source_pdf, page_num):
    """Extract definitions that have bullet points or multi-line structure"""
    definitions = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = clean_text(lines[i])
        
        # Look for potential term (short line, not ending with period)
        if (len(line) > 2 and len(line) < 60 and 
            not line.endswith('.') and
            not line.endswith('?') and
            not re.search(r'\d{4}', line) and  # Skip years
            not re.search(r'(?:page|section|chapter|act|law)', line, re.IGNORECASE)):
            
            # Check if next lines contain bullet points or explanations
            explanation_lines = []
            j = i + 1
            
            # Look for bullet points or indented explanations in next few lines
            while j < len(lines) and j < i + 10:  # Look ahead up to 10 lines
                next_line = clean_text(lines[j])
                
                if not next_line:
                    j += 1
                    continue
                
                # Stop if we hit another major term (capitalized, short, not ending with period)
                if (len(next_line) > 2 and len(next_line) < 50 and 
                    next_line[0].isupper() and 
                    not next_line.endswith('.') and
                    not re.search(r'(?:is|are|means|refers|defined|described)', next_line, re.IGNORECASE) and
                    not next_line.startswith('•') and
                    not next_line.startswith('-')):
                    break
                
                # Include if it's a bullet point or looks like an explanation
                if (next_line.startswith('•') or 
                    next_line.startswith('-') or
                    next_line.startswith('*') or
                    re.match(r'^\d+\.', next_line) or
                    re.search(r'(?:and|but|or|so|because|since|however|therefore|also|in addition|furthermore|sharing|little|no longer|joint|several)', next_line, re.IGNORECASE) or
                    len(next_line.split()) > 4):
                    
                    explanation_lines.append(next_line)
                
                j += 1
            
            # If we found substantial bullet points or explanations
            if len(explanation_lines) >= 2:
                # Clean up the term
                term = line.strip(' :-')
                term = re.sub(r'^\d+\.?\s*', '', term)  # Remove leading numbers
                
                # Format explanations nicely
                explanations = []
                for exp in explanation_lines:
                    exp = exp.lstrip('•-*0123456789.- ').strip()
                    if exp:
                        explanations.append(exp)
                
                if explanations and term and len(term) > 2:
                    definitions.append({
                        'term': term,
                        'explanations': explanations,
                        'source_pdf': source_pdf,
                        'page': page_num + 1,
                        'line_count': len(explanations)
                    })
                    
                    i = j - 1  # Skip ahead
        
        i += 1
    
    return definitions

def main():
    print("🎯 BULLET POINT DEFINITION SCRAPER - Looking for term + bullet points...")
    
    all_definitions = []
    
    # Loop through all PDFs
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            print(f"📄 Scanning: {filename}")
            pdf_path = os.path.join(pdf_folder, filename)
            
            try:
                doc = fitz.open(pdf_path)
                
                for page_num, page in enumerate(doc):
                    text = page.get_text("text")
                    if text.strip():
                        page_defs = extract_bullet_point_definitions(text, filename, page_num)
                        all_definitions.extend(page_defs)
                
                doc.close()
                
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                continue
    
    # Remove duplicates based on term similarity
    unique_definitions = []
    seen_terms = set()
    
    for def_item in all_definitions:
        term_key = def_item['term'].lower().replace(' ', '').replace('-', '')
        if term_key not in seen_terms:
            seen_terms.add(term_key)
            unique_definitions.append(def_item)
    
    # Sort by term
    unique_definitions.sort(key=lambda x: x['term'])
    
    # Save to CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Explanation 1", "Explanation 2", "Explanation 3", "Explanation 4", "Source PDF", "Page", "Line Count"])
        
        for def_item in unique_definitions:
            # Pad explanations to have consistent columns
            explanations = def_item['explanations'] + [''] * 4
            explanations = explanations[:4]  # Take max 4
            
            writer.writerow([
                def_item['term'],
                explanations[0],
                explanations[1], 
                explanations[2],
                explanations[3],
                def_item['source_pdf'],
                def_item['page'],
                def_item['line_count']
            ])
    
    print(f"\n🎯 BULLET POINT EXTRACTION COMPLETE!")
    print(f"📊 Found {len(unique_definitions)} bullet-point definitions")
    print(f"💾 Saved to: {output_csv}")
    
    # Show the best examples
    print(f"\n🎯 BEST EXAMPLES:")
    good_examples = [d for d in unique_definitions if d['line_count'] >= 3]
    for i, def_item in enumerate(good_examples[:10]):
        print(f"{i+1:2d}. {def_item['term']} ({def_item['line_count']} points)")
        for j, exp in enumerate(def_item['explanations'][:3]):
            print(f"    • {exp}")
        print(f"    From: {def_item['source_pdf']} page {def_item['page']}")
        print()

if __name__ == "__main__":
    main()
