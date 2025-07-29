#!/usr/bin/env python3
"""
Script to convert Markdown documentation to PDF
"""

import os
import sys
import markdown
from pathlib import Path

def create_html_from_markdown(markdown_file):
    """Convert Markdown to HTML with custom styling"""
    
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=[
            'markdown.extensions.toc',
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.attr_list'
        ]
    )
    
    # Create full HTML document with styling
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gmail, Calendar, and Maps MCP Server - Complete Explanation</title>
    <style>
        @page {{
            margin: 1in;
            size: A4;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 30px;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #7f8c8d;
            margin-top: 25px;
            page-break-after: avoid;
        }}
        
        h4 {{
            color: #95a5a6;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 5px 0;
        }}
        
        .toc a {{
            text-decoration: none;
            color: #3498db;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        
        .warning {{
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
        }}
        
        .success {{
            background-color: #d4edda;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            margin: 15px 0;
        }}
        
        .info {{
            background-color: #d1ecf1;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #17a2b8;
            margin: 15px 0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        @media print {{
            body {{
                font-size: 12pt;
            }}
            
            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}
            
            pre, table, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
    
    return html_template

def convert_to_pdf(html_content, output_file):
    """Convert HTML to PDF using weasyprint"""
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Create PDF from HTML
        HTML(string=html_content).write_pdf(
            output_file,
            font_config=font_config
        )
        
        print(f"✅ PDF generated successfully: {output_file}")
        return True
        
    except ImportError:
        print("❌ weasyprint not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
            
            # Try again after installation
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            font_config = FontConfiguration()
            HTML(string=html_content).write_pdf(output_file, font_config=font_config)
            
            print(f"✅ PDF generated successfully: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install weasyprint: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

def main():
    """Main function to convert markdown to PDF"""
    
    # File paths
    docs_dir = Path(__file__).parent
    markdown_file = docs_dir / "mcp-server-explanation.md"
    output_file = docs_dir / "mcp-server-explanation.pdf"
    
    print("🚀 Converting Markdown to PDF...")
    print(f"📄 Input: {markdown_file}")
    print(f"📄 Output: {output_file}")
    
    # Check if markdown file exists
    if not markdown_file.exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return False
    
    # Convert markdown to HTML
    print("📝 Converting Markdown to HTML...")
    html_content = create_html_from_markdown(markdown_file)
    
    # Convert HTML to PDF
    print("🖨️ Converting HTML to PDF...")
    success = convert_to_pdf(html_content, output_file)
    
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