import csv
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap

def clean_text_advanced(text):
    """Advanced text cleaning to handle all edge cases"""
    if not text:
        return ""
    
    # Remove various bullet characters and symbols
    bullet_chars = ['•', '▪', '▫', '◦', '‣', '⁃', '■', '●', '○', '◆', '◇', '✓', '✗', '→', '←', '↑', '↓']
    for char in bullet_chars:
        text = text.replace(char, '')
    
    # Clean up quotes and apostrophes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Clean up excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common formatting issues
    text = text.replace(' , ', ', ').replace(' . ', '. ')
    
    # Remove page numbers and citations that got mixed in
    text = re.sub(r'\s*\d+\s*$', '', text)  # trailing numbers
    text = re.sub(r'^\d+\s*', '', text)     # leading numbers
    
    return text.strip()

def split_into_paragraphs(text, max_chars_per_para=300):
    """Intelligently split long text into readable paragraphs"""
    if not text:
        return []
    
    # First try to split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    paragraphs = []
    current_para = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If sentence is very long, split it further
        if len(sentence) > max_chars_per_para:
            if current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
                current_length = 0
            
            # Split long sentence by clauses
            clauses = re.split(r'(?<=,)\s+|(?<=;)\s+', sentence)
            for clause in clauses:
                clause = clause.strip()
                if len(clause) > max_chars_per_para:
                    # Split by words if still too long
                    words = clause.split()
                    temp_clause = []
                    temp_length = 0
                    
                    for word in words:
                        if temp_length + len(word) + 1 > max_chars_per_para and temp_clause:
                            paragraphs.append(' '.join(temp_clause))
                            temp_clause = [word]
                            temp_length = len(word)
                        else:
                            temp_clause.append(word)
                            temp_length += len(word) + 1
                    
                    if temp_clause:
                        current_para.extend(temp_clause)
                        current_length = sum(len(w) + 1 for w in temp_clause)
                else:
                    if current_length + len(clause) + 1 > max_chars_per_para and current_para:
                        paragraphs.append(' '.join(current_para))
                        current_para = [clause]
                        current_length = len(clause)
                    else:
                        current_para.append(clause)
                        current_length += len(clause) + 1
        else:
            if current_length + len(sentence) + 1 > max_chars_per_para and current_para:
                paragraphs.append(' '.join(current_para))
                current_para = [sentence]
                current_length = len(sentence)
            else:
                current_para.append(sentence)
                current_length += len(sentence) + 1
    
    if current_para:
        paragraphs.append(' '.join(current_para))
    
    return paragraphs

def create_advanced_pdf_from_csv(csv_file, output_pdf):
    """Create an advanced, perfectly formatted PDF from CSV data"""
    
    # Set up the document with better margins
    doc = SimpleDocTemplate(
        output_pdf, 
        pagesize=A4,
        rightMargin=60, 
        leftMargin=60,
        topMargin=60, 
        bottomMargin=40,
        allowSplitting=1
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        spaceBefore=20,
        textColor=darkblue,
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    
    case_style = ParagraphStyle(
        'CaseName',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=25,
        textColor=darkblue,
        leftIndent=0,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=black,
        borderPadding=5
    )
    
    explanation_style = ParagraphStyle(
        'Explanation',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        spaceBefore=5,
        leftIndent=25,
        rightIndent=25,
        leading=15,
        fontName='Helvetica',
        textColor=black
    )
    
    source_style = ParagraphStyle(
        'Source',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=20,
        spaceBefore=5,
        leftIndent=25,
        rightIndent=25,
        leading=12,
        fontName='Helvetica-Oblique',
        textColor=darkblue
    )
    
    # Build the story (content)
    story = []
    
    # Add title page
    story.append(Paragraph("Legal Cases Compilation", title_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Comprehensive collection of legal cases with detailed explanations", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], 
                                        fontSize=12, alignment=1, spaceAfter=50)))
    story.append(PageBreak())
    
    # Read CSV and add content
    case_count = 0
    total_cases = 0
    
    # First pass to count total cases
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        total_cases = sum(1 for row in reader if len(row) >= 3 and row[0].strip() and row[1].strip())
    
    # Second pass to process content
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        
        for row_num, row in enumerate(reader, 1):
            if len(row) >= 3:
                case_name = clean_text_advanced(row[0].strip())
                explanation = clean_text_advanced(row[1].strip())
                source_pdf = clean_text_advanced(row[2].strip())
                
                if case_name and explanation:
                    # Add case name with proper formatting
                    story.append(Paragraph(f"<b>{case_name}</b>", case_style))
                    
                    # Split explanation into readable paragraphs
                    paragraphs = split_into_paragraphs(explanation, 350)
                    
                    for para in paragraphs:
                        if para.strip():
                            # Ensure proper sentence endings
                            if not para.endswith(('.', '!', '?', '"', "'")):
                                para += '.'
                            story.append(Paragraph(para, explanation_style))
                    
                    # Add source information
                    if source_pdf:
                        source_text = f"Source: {source_pdf.replace('.pdf', '')}"
                        story.append(Paragraph(f"<i>{source_text}</i>", source_style))
                    
                    case_count += 1
                    
                    # Add progress indicator (every 20 cases)
                    if case_count % 20 == 0:
                        print(f"Processed {case_count}/{total_cases} cases...")
                    
                    # Add page break every 8 cases for better readability
                    if case_count % 8 == 0 and case_count < total_cases:
                        story.append(PageBreak())
    
    # Build the PDF
    print("Building PDF...")
    doc.build(story)
    
    print(f"✅ PDF created successfully: {output_pdf}")
    print(f"📊 Total cases included: {case_count}")
    print(f"📄 PDF pages: ~{max(1, case_count // 8)}")
    
    return case_count

if __name__ == "__main__":
    input_csv = "legal_cases_with_sources.csv"
    output_pdf = "Advanced_Legal_Cases_with_Sources.pdf"
    
    print("🚀 Starting advanced PDF generation...")
    print(f"📖 Reading from: {input_csv}")
    print(f"📝 Writing to: {output_pdf}")
    print()
    
    try:
        cases_processed = create_advanced_pdf_from_csv(input_csv, output_pdf)
        print(f"\n🎉 Success! Processed {cases_processed} cases into a clean PDF.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
