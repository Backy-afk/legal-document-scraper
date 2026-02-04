import fitz  # PyMuPDF
import re
import csv
import os

# SETTINGS
pdf_folder = r"C:\Users\BACKY\Downloads\FILENAME"      # Folder containing all your PDFs
output_csv = "legal_cases_with_sources.csv"

# More comprehensive regex for case names
case_patterns = [
    re.compile(r"[A-Z][a-zA-Z]+ v\.? [A-Z][a-zA-Z]+(?:\s*\[\d{4}\])?"),
    re.compile(r"[A-Z][a-zA-Z]+ [Vv] [A-Z][a-zA-Z]+(?:\s*\[\d{4}\])?"),
    re.compile(r"[A-Z][a-zA-Z]+ and [A-Z][a-zA-Z]+(?:\s*\[\d{4}\])?"),
]

def clean_text(text):
    """Remove weird characters and clean up text"""
    # Remove common bullet characters
    text = text.replace('', '').replace('•', '').replace('▪', '').replace('▫', '')
    # Clean up extra whitespace but keep line breaks for processing
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

cases = []

print("Scanning PDFs for cases...")

# Loop through all PDFs in folder
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        print(f"Processing: {filename}")
        pdf_path = os.path.join(pdf_folder, filename)
        doc = fitz.open(pdf_path)

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            text = clean_text(text)
            lines = text.split("\n")

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                    
                # Try all case patterns
                match_found = False
                for pattern in case_patterns:
                    match = pattern.search(line)
                    if match:
                        case_name = match.group().strip()
                        explanation_lines = []

                        # Grab text immediately after case name
                        j = i + 1
                        while j < len(lines):
                            next_line = clean_text(lines[j])
                            if not next_line:
                                j += 1
                                continue
                            
                            # Stop if we hit another case or end of content
                            if any(p.search(next_line) for p in case_patterns):
                                break
                            # Stop if line looks like a page number or citation
                            if re.match(r'^\d+$|^Page \d+|^\[\d{4}\]$', next_line):
                                break
                            # Stop if line is very short (likely fragment)
                            if len(next_line) < 10:
                                j += 1
                                continue
                                
                            explanation_lines.append(next_line)
                            j += 1

                        explanation = " ".join(explanation_lines).strip()
                        if explanation and len(explanation) > 20:  # Only keep substantial explanations
                            cases.append((case_name, explanation, filename))  # Add source PDF
                            i = j
                            match_found = True
                            break
                
                if not match_found:
                    i += 1

        doc.close()

# Remove duplicates while preserving order
seen = set()
unique_cases = []
for case, explanation, source_pdf in cases:
    if case not in seen:
        seen.add(case)
        unique_cases.append((case, explanation, source_pdf))

# Save all cases to a single CSV with source information
with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Case Name", "Explanation", "Source PDF"])
    for case_name, explanation, source_pdf in unique_cases:
        writer.writerow([case_name, explanation, source_pdf])


print(f"Done! Found {len(unique_cases)} unique cases saved to '{output_csv}'.")
