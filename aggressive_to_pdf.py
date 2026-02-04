import csv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, darkblue

def clean_text(text):
    if not text:
        return ""
    # Remove weird characters
    text = text.replace('"', '').replace('"', '').replace('"', '').replace('"', '')
    text = text.replace(''', "'").replace(''', "'")
    # Clean up spacing
    text = ' '.join(text.split())
    return text.strip()

def create_aggressive_pdf(csv_file, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=darkblue, alignment=1)
    term_style = ParagraphStyle('Term', parent=styles['Heading2'], fontSize=12, spaceAfter=8, spaceBefore=15, textColor=darkblue)
    definition_style = ParagraphStyle('Definition', parent=styles['Normal'], fontSize=10, spaceAfter=12, leftIndent=15, rightIndent=15)
    source_style = ParagraphStyle('Source', parent=styles['Normal'], fontSize=8, spaceAfter=15, leftIndent=15, rightIndent=15, textColor=darkblue)
    
    story = []
    story.append(Paragraph("Complete Definition Collection", title_style))
    story.append(Paragraph("All extracted definitions from legal documents", ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, alignment=1, spaceAfter=30)))
    story.append(PageBreak())
    
    count = 0
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        
        for row in reader:
            if len(row) >= 3:
                term = clean_text(row[0])
                definition = clean_text(row[1])
                source = clean_text(row[2])
                
                if term and definition:
                    story.append(Paragraph(f"<b>{term}</b>", term_style))
                    
                    # Split long definitions
                    if len(definition) > 300:
                        sentences = definition.split('. ')
                        for sent in sentences:
                            if sent.strip():
                                if not sent.endswith('.'):
                                    sent += '.'
                                story.append(Paragraph(sent, definition_style))
                    else:
                        story.append(Paragraph(definition, definition_style))
                    
                    if source:
                        story.append(Paragraph(f"<i>Source: {source}</i>", source_style))
                    
                    count += 1
                    if count % 20 == 0:
                        story.append(PageBreak())
    
    doc.build(story)
    print(f"✅ Created PDF with {count} definitions: {output_pdf}")
    return count

if __name__ == "__main__":
    create_aggressive_pdf("every_single_definition.csv", "Complete_Definitions.pdf")
