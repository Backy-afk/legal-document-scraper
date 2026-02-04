import fitz  # PyMuPDF
import re
import csv
import os

# SETTINGS
pdf_folder = r"C:\Users\bella\Downloads\compressed"      # Folder containing all your PDFs
output_csv = "structured_definitions.csv"

def clean_text(text):
    """Basic text cleaning"""
    if not text:
        return ""
    text = re.sub(r'[•▪▫◦‣⁃■●○◆◇]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def extract_structured_definitions(text, source_pdf, page_num):
    """Extract definitions with bullet points or multi-line explanations"""
    definitions = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = clean_text(lines[i])
        
        # Look for potential term headers (short, capitalized, followed by explanation)
        if (len(line) > 3 and len(line) < 50 and 
            (line[0].isupper() or line.startswith('•') or re.match(r'^\d+\.', line)) and
            not line.endswith('.') and
            not re.search(r'(?:the|and|or|but|in|on|at|to|for|with|by|from|up|about|into|through|during|before|after|above|below|between|among|under|over|above)\s*$', line.lower())):
            
            term = line.lstrip('•0123456789.- ').strip()
            
            # Look ahead for bullet points or explanations
            explanation_lines = []
            j = i + 1
            
            # Collect next few lines that look like explanations
            while j < len(lines) and j < i + 8:  # Look at next 7 lines max
                next_line = clean_text(lines[j])
                
                # Stop conditions
                if not next_line:
                    j += 1
                    continue
                    
                # Stop if we hit another major term (capitalized, short)
                if (len(next_line) > 3 and len(next_line) < 40 and 
                    next_line[0].isupper() and 
                    not next_line.endswith('.') and
                    not re.search(r'(?:is|are|means|refers|defined|described)', next_line, re.IGNORECASE)):
                    break
                
                # Stop if we hit a page number or section header
                if re.match(r'^(?:Page \d+|\d+|Section|Chapter)', next_line, re.IGNORECASE):
                    break
                
                # Include this line if it looks like an explanation
                if (len(next_line) > 5 and 
                    (next_line.startswith(('•', '-', '*', '–', '—')) or
                     re.match(r'^\d+\.', next_line) or
                     re.search(r'(?:and|but|or|so|because|since|however|therefore|also|in addition|furthermore)', next_line, re.IGNORECASE) or
                     len(next_line.split()) > 3)):
                    
                    explanation_lines.append(next_line)
                
                j += 1
            
            # If we found substantial explanations, save it
            if len(explanation_lines) >= 2:  # At least 2 explanation lines
                full_explanation = ' | '.join(explanation_lines)
                
                # Clean up the term
                term = re.sub(r'^\d+\.?\s*', '', term)  # Remove leading numbers
                term = term.strip(' :-')
                
                if term and len(term) > 2:
                    definitions.append({
                        'term': term,
                        'explanation': full_explanation,
                        'source_pdf': source_pdf,
                        'page': page_num + 1,
                        'lines_found': len(explanation_lines)
                    })
                    
                    i = j - 1  # Skip ahead since we processed these lines
        else:
            # Also look for "Term:" followed by explanations
            colon_match = re.match(r'^([A-Z][a-zA-Z\s]+):?\s*$', line)
            if colon_match:
                term = colon_match.group(1).strip()
                
                # Look for explanations after the colon
                explanation_lines = []
                j = i + 1
                
                while j < len(lines) and j < i + 6:
                    next_line = clean_text(lines[j])
                    if next_line and len(next_line) > 5:
                        explanation_lines.append(next_line)
                    elif not next_line:
                        j += 1
                        continue
                    else:
                        break
                    j += 1
                
                if len(explanation_lines) >= 2:
                    definitions.append({
                        'term': term,
                        'explanation': ' | '.join(explanation_lines),
                        'source_pdf': source_pdf,
                        'page': page_num + 1,
                        'lines_found': len(explanation_lines)
                    })
                    i = j - 1
        
        i += 1
    
    return definitions

def main():
    print("🎯 STRUCTURED DEFINITION SCRAPER - Looking for multi-line explanations...")
    
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
                        page_defs = extract_structured_definitions(text, filename, page_num)
                        all_definitions.extend(page_defs)
                
                doc.close()
                
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                continue
    
    # Remove duplicates
    unique_definitions = []
    seen = set()
    
    for def_item in all_definitions:
        key = def_item['term'].lower()
        if key not in seen:
            seen.add(key)
            unique_definitions.append(def_item)
    
    # Sort by term
    unique_definitions.sort(key=lambda x: x['term'])
    
    # Save to CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Explanation", "Source PDF", "Page", "Lines Found"])
        
        for def_item in unique_definitions:
            writer.writerow([
                def_item['term'],
                def_item['explanation'],
                def_item['source_pdf'],
                def_item['page'],
                def_item['lines_found']
            ])
    
    print(f"\n🎯 STRUCTURED EXTRACTION COMPLETE!")
    print(f"📊 Found {len(unique_definitions)} structured definitions")
    print(f"💾 Saved to: {output_csv}")
    
    # Show examples
    print(f"\n🎯 EXAMPLES FOUND:")
    for i, def_item in enumerate(unique_definitions[:10]):
        print(f"{i+1:2d}. {def_item['term']}")
        print(f"    {def_item['explanation'][:80]}...")
        print(f"    ({def_item['lines_found']} lines from {def_item['source_pdf']})")
        print()

if __name__ == "__main__":
    main()
