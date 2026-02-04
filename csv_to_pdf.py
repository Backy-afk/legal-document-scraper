import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue
import textwrap

def create_pdf_from_csv(csv_file, output_pdf):
    """Create a clean PDF from the CSV case data"""
    
    # Set up the document
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=darkblue,
        alignment=1  # Center
    )
    
    case_style = ParagraphStyle(
        'CaseName',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=darkblue,
        leftIndent=0
    )
    
    explanation_style = ParagraphStyle(
        'Explanation',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20,
        leftIndent=20,
        rightIndent=20,
        leading=14
    )
    
    # Build the story (content)
    story = []
    
    # Add title
    story.append(Paragraph("Legal Cases Compilation", title_style))
    story.append(Spacer(1, 20))
    
    # Read CSV and add content
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        
        case_count = 0
        for row in reader:
            if len(row) >= 2:
                case_name = row[0].strip()
                explanation = row[1].strip()
                
                if case_name and explanation:
                    # Add case name
                    story.append(Paragraph(f"<b>{case_name}</b>", case_style))
                    
                    # Clean and format explanation
                    # Replace problematic characters and format
                    explanation = explanation.replace('"', '')
                    explanation = explanation.replace("'", "'")
                    
                    # Split long explanations into paragraphs
                    sentences = explanation.split('. ')
                    for sentence in sentences:
                        if sentence.strip():
                            if not sentence.endswith('.'):
                                sentence += '.'
                            story.append(Paragraph(sentence, explanation_style))
                    
                    case_count += 1
                    
                    # Add page break every 10 cases for better readability
                    if case_count % 10 == 0:
                        story.append(PageBreak())
    
    # Build the PDF
    doc.build(story)
    print(f"PDF created successfully: {output_pdf}")
    print(f"Total cases included: {case_count}")

if __name__ == "__main__":
    input_csv = "legal_cases_clean.csv"
    output_pdf = "Legal_Cases_Compilation.pdf"
    
    create_pdf_from_csv(input_csv, output_pdf)
