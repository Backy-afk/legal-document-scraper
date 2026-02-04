import fitz  # PyMuPDF
import re
import csv
import os

# SETTINGS
pdf_folder = r"C:\Users\BACKY\Downloads\YOUR-FILE-NAME"      # Folder containing all your PDFs
output_csv = "every_single_definition.csv"

def clean_text(text):
    """Basic text cleaning"""
    if not text:
        return ""
    text = re.sub(r'[•▪▫◦‣⁃■●○◆◇]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def extract_anything_that_looks_like_definition(text, source_pdf, page_num):
    """Extract ANYTHING that could be a definition - be super aggressive"""
    definitions = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = clean_text(line)
        if len(line) < 10:
            continue
        
        # ANY line that has these patterns = probably a definition
        definition_indicators = [
            r'(.+?)\s+(?:is|are|means?|refers? to|can be defined as|described as|defined as|involves|consists of|includes|comprises)\s+(.+)',
            r'(?:A|An|The)\s+(.+?)\s+(?:is|means?|refers? to)\s+(.+)',
            r'(.+?)\s*[:\-]\s+(.+)',  # Term: Definition
            r'What\s+(?:is|are)\s+(.+?)\??\s*(?:[:\-]?\s*(.+))?',
            r'Definition[:\s]*(.+?)\s*(?:[:\-]?\s*(.+))?',
            r'(.+?)\s+can\s+be\s+(?:described|explained)\s+as\s+(.+)',
        ]
        
        for pattern in definition_indicators:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    term = clean_text(groups[0])
                    definition = clean_text(groups[1])
                    
                    if term and definition and len(term) > 2 and len(definition) > 10:
                        # Look for more text in next few lines
                        full_def = definition
                        j = i + 1
                        while j < len(lines) and j < i + 4:
                            next_line = clean_text(lines[j])
                            if next_line and len(next_line) > 15:
                                # Stop if we hit another definition-like line
                                if re.search(r'(?:is|means|refers|defined|described)', next_line, re.IGNORECASE):
                                    break
                                full_def += " " + next_line
                                j += 1
                            else:
                                break
                        
                        definitions.append({
                            'term': term,
                            'definition': full_def,
                            'source_pdf': source_pdf,
                            'page': page_num + 1,
                            'raw_line': line
                        })
    
    return definitions

def main():
    print("🔥 AGGRESSIVE MODE: Extracting EVERYTHING that looks like a definition...")
    
    all_definitions = []
    
    # Loop through all PDFs
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            print(f"📄 RIPPING: {filename}")
            pdf_path = os.path.join(pdf_folder, filename)
            
            try:
                doc = fitz.open(pdf_path)
                
                for page_num, page in enumerate(doc):
                    text = page.get_text("text")
                    if text.strip():
                        page_defs = extract_anything_that_looks_like_definition(text, filename, page_num)
                        all_definitions.extend(page_defs)
                
                doc.close()
                
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                continue
    
    # Remove duplicates
    unique_definitions = []
    seen = set()
    
    for def_item in all_definitions:
        key = (def_item['term'].lower(), def_item['definition'].lower()[:50])
        if key not in seen:
            seen.add(key)
            unique_definitions.append(def_item)
    
    # Sort by term
    unique_definitions.sort(key=lambda x: x['term'])
    
    # Save to CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Definition", "Source PDF", "Page", "Raw Line"])
        
        for def_item in unique_definitions:
            writer.writerow([
                def_item['term'],
                def_item['definition'],
                def_item['source_pdf'],
                def_item['page'],
                def_item['raw_line']
            ])
    
    print(f"\n🔥 AGGRESSIVE EXTRACTION COMPLETE!")
    print(f"📊 Found {len(unique_definitions)} potential definitions")
    print(f"💾 Saved to: {output_csv}")
    
    # Show first 20 results
    print(f"\n🔥 FIRST 20 RESULTS:")
    for i, def_item in enumerate(unique_definitions[:20]):
        print(f"{i+1:2d}. {def_item['term'][:30]:30s} = {def_item['definition'][:60]}...")

if __name__ == "__main__":
    main()
