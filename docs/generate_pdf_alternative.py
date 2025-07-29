#!/usr/bin/env python3
"""
Alternative script to convert Markdown documentation to PDF using reportlab
"""

import os
import sys
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

def parse_markdown_sections(markdown_file):
    """Parse markdown file into sections"""
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into sections based on headers
    sections = []
    lines = content.split('\n')
    current_section = {'title': '', 'content': [], 'level': 0}
    
    for line in lines:
        # Check for headers
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            # Save previous section if it exists
            if current_section['title']:
                sections.append(current_section.copy())
            
            # Start new section
            level = len(header_match.group(1))
            title = header_match.group(2)
            current_section = {
                'title': title,
                'content': [],
                'level': level
            }
        else:
            # Add line to current section
            if line.strip() or current_section['content']:
                current_section['content'].append(line)
    
    # Add the last section
    if current_section['title']:
        sections.append(current_section)
    
    return sections

def create_pdf_styles():
    """Create custom styles for the PDF"""
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#34495e'),
        borderWidth=1,
        borderColor=colors.HexColor('#3498db'),
        borderPadding=5
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#7f8c8d')
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#95a5a6')
    ))
    
    styles.add(ParagraphStyle(
        name='CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leftIndent=20,
        rightIndent=20,
        backColor=colors.HexColor('#f8f9fa'),
        borderWidth=1,
        borderColor=colors.HexColor('#e9ecef'),
        borderPadding=10
    ))
    
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    ))
    
    return styles

def process_markdown_content(content_lines, styles):
    """Process markdown content into PDF elements"""
    elements = []
    
    for line in content_lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 6))
            continue
        
        # Handle code blocks
        if line.startswith('```'):
            continue  # Skip code block markers
        
        # Handle inline code
        if '`' in line:
            line = re.sub(r'`([^`]+)`', r'<code>\1</code>', line)
        
        # Handle bold text
        line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
        
        # Handle italic text
        line = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', line)
        
        # Handle links
        line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        
        # Check if it's a code block (indented or has specific markers)
        if line.startswith('    ') or line.startswith('\t'):
            elements.append(Paragraph(line, styles['CodeBlock']))
        else:
            elements.append(Paragraph(line, styles['NormalText']))
    
    return elements

def create_table_of_contents(sections):
    """Create a table of contents"""
    toc_elements = []
    toc_elements.append(Paragraph("Table of Contents", getSampleStyleSheet()['Heading1']))
    toc_elements.append(Spacer(1, 20))
    
    for i, section in enumerate(sections):
        if section['level'] <= 2:  # Only include main sections
            indent = (section['level'] - 1) * 20
            toc_elements.append(Paragraph(
                f"{'&nbsp;' * indent}• {section['title']}",
                getSampleStyleSheet()['Normal']
            ))
            toc_elements.append(Spacer(1, 6))
    
    toc_elements.append(PageBreak())
    return toc_elements

def generate_pdf(markdown_file, output_file):
    """Generate PDF from markdown file"""
    
    # Parse markdown sections
    sections = parse_markdown_sections(markdown_file)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = create_pdf_styles()
    
    # Build PDF content
    story = []
    
    # Add title page
    story.append(Paragraph("Gmail, Calendar, and Maps MCP Server", styles['CustomTitle']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Complete Explanation & Documentation", styles['CustomHeading2']))
    story.append(Spacer(1, 50))
    story.append(Paragraph("A comprehensive guide to understanding, setting up, and using the MCP server that integrates Gmail, Google Calendar, and Google Maps functionality.", styles['NormalText']))
    story.append(PageBreak())
    
    # Add table of contents
    story.extend(create_table_of_contents(sections))
    
    # Add sections
    for section in sections:
        # Add section header
        if section['level'] == 1:
            story.append(Paragraph(section['title'], styles['CustomHeading1']))
        elif section['level'] == 2:
            story.append(Paragraph(section['title'], styles['CustomHeading2']))
        elif section['level'] == 3:
            story.append(Paragraph(section['title'], styles['CustomHeading3']))
        else:
            story.append(Paragraph(section['title'], styles['NormalText']))
        
        # Add section content
        content_elements = process_markdown_content(section['content'], styles)
        story.extend(content_elements)
        
        # Add page break for major sections
        if section['level'] <= 2:
            story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    
    return True

def main():
    """Main function"""
    
    # File paths
    docs_dir = Path(__file__).parent
    markdown_file = docs_dir / "mcp-server-explanation.md"
    output_file = docs_dir / "mcp-server-explanation.pdf"
    
    print("🚀 Converting Markdown to PDF (Alternative Method)...")
    print(f"📄 Input: {markdown_file}")
    print(f"📄 Output: {output_file}")
    
    # Check if markdown file exists
    if not markdown_file.exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return False
    
    try:
        # Try to import reportlab
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
            
            # Try importing again
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
            
        except Exception as e:
            print(f"❌ Failed to install reportlab: {e}")
            return False
    
    # Generate PDF
    print("📝 Converting Markdown to PDF...")
    success = generate_pdf(markdown_file, output_file)
    
    if success:
        print(f"\n🎉 Success! PDF created: {output_file}")
        print(f"📏 File size: {output_file.stat().st_size / 1024:.1f} KB")
        
        # Open the PDF if possible
        try:
            import platform
            if platform.system() == "Darwin":  # macOS
                os.system(f"open {output_file}")
            elif platform.system() == "Windows":
                os.system(f"start {output_file}")
            elif platform.system() == "Linux":
                os.system(f"xdg-open {output_file}")
        except:
            pass
    else:
        print("❌ Failed to generate PDF")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 