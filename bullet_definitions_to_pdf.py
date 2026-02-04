import csv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, darkblue

def clean_text(text):
    """Clean text for PDF"""
    if not text:
        return ""
    # Remove weird characters
    text = text.replace('"', '').replace('"', '').replace('"', '').replace('"', '')
    text = text.replace(''', "'").replace(''', "'")
    # Clean up spacing
    text = ' '.join(text.split())
    return text.strip()

def create_bullet_definitions_pdf(csv_file, output_pdf):
    """Create PDF from bullet point definitions CSV"""
    
    doc = SimpleDocTemplate(
        output_pdf, 
        pagesize=A4,
        rightMargin=50, 
        leftMargin=50,
        topMargin=50, 
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        spaceBefore=20,
        textColor=darkblue,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    term_style = ParagraphStyle(
        'Term',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=darkblue,
        leftIndent=0,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=5,
        leftIndent=30,
        rightIndent=20,
        leading=14,
        fontName='Helvetica',
        textColor=black
    )
    
    source_style = ParagraphStyle(
        'Source',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=20,
        spaceBefore=5,
        leftIndent=20,
        rightIndent=20,
        leading=12,
        fontName='Helvetica-Oblique',
        textColor=darkblue
    )
    
    # Build the story (content)
    story = []
    
    # Add title page
    story.append(Paragraph("Structured Definitions", title_style))
    story.append(Paragraph("Legal and Business Terms with Detailed Explanations", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], 
                                        fontSize=12, alignment=1, spaceAfter=40)))
    story.append(PageBreak())
    
    definition_count = 0
    
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        
        for row_num, row in enumerate(reader, 1):
            if len(row) >= 6:
                term = clean_text(row[0])
                explanations = [clean_text(exp) for exp in row[1:5] if exp]  # First 4 explanation columns
                source_pdf = clean_text(row[5])
                page = row[6] if len(row) > 6 else ""
                line_count = row[7] if len(row) > 7 else ""
                
                if term and explanations:
                    # Add term name
                    story.append(Paragraph(f"<b>{term}</b>", term_style))
                    
                    # Add bullet points
                    for exp in explanations:
                        if exp and exp.strip():
                            # Format as bullet point
                            bullet_text = f"• {exp}"
                            # Handle long text by splitting sentences
                            if len(exp) > 200:
                                sentences = exp.split('. ')
                                for i, sent in enumerate(sentences):
                                    if sent.strip():
                                        if i == 0:
                                            story.append(Paragraph(f"• {sent.strip()}.", bullet_style))
                                        else:
                                            story.append(Paragraph(f"  {sent.strip()}.", bullet_style))
                            else:
                                story.append(Paragraph(bullet_text, bullet_style))
                    
                    # Add source information
                    source_text = f"Source: {source_pdf.replace('.pdf', '')}"
                    if page:
                        source_text += f" (Page {page})"
                    if line_count:
                        source_text += f" - {line_count} points"
                    
                    story.append(Paragraph(f"<i>{source_text}</i>", source_style))
                    
                    definition_count += 1
                    
                    # Add page break every 15 definitions for better readability
                    if definition_count % 15 == 0:
                        story.append(PageBreak())
    
    # Build the PDF
    print("Building bullet point definitions PDF...")
    doc.build(story)
    
    print(f"✅ PDF created successfully: {output_pdf}")
    print(f"📊 Total definitions included: {definition_count}")
    print(f"📄 PDF pages: ~{max(1, definition_count // 15)}")
    
    return definition_count

if __name__ == "__main__":
    input_csv = "bullet_point_definitions.csv"
    output_pdf = "Structured_Definitions.pdf"
    
    print("🚀 Creating PDF from bullet point definitions...")
    print(f"📖 Reading from: {input_csv}")
    print(f"📝 Writing to: {output_pdf}")
    print()
    
    try:
        defs_processed = create_bullet_definitions_pdf(input_csv, output_pdf)
        print(f"\n🎉 Success! Created PDF with {defs_processed} structured definitions.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
