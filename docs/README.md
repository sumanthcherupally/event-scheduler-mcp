# Documentation

This directory contains comprehensive documentation for the Gmail, Calendar, and Maps MCP Server.

## Files

### 📄 `mcp-server-explanation.md`
The complete explanation document in Markdown format. This is the source file for the PDF documentation.

### 📄 `mcp-server-explanation.pdf`
The complete explanation document converted to PDF format. This is a professionally formatted document with:
- Table of contents
- Proper styling and formatting
- Code examples
- Diagrams and explanations
- Best practices and troubleshooting guides

### 🛠️ `generate_pdf.py`
Script to convert the Markdown file to PDF using weasyprint (may have dependency issues on some systems).

### 🛠️ `generate_pdf_alternative.py`
Alternative script to convert the Markdown file to PDF using reportlab (more reliable across different systems).

## Generating the PDF

To regenerate the PDF from the Markdown file:

```bash
# Using the alternative method (recommended)
python generate_pdf_alternative.py

# Or using weasyprint (may require additional system dependencies)
python generate_pdf.py
```

## PDF Contents

The PDF document includes:

1. **Introduction** - What the MCP server does and its benefits
2. **What is MCP?** - Explanation of the Model Context Protocol
3. **Architecture Overview** - How the system is structured
4. **Core Components** - Detailed explanation of each component
5. **Authentication & Security** - OAuth 2.0 and security features
6. **Available Tools** - Complete documentation of all 7 MCP tools
7. **Usage Examples** - Practical examples for each service
8. **Integration Workflows** - How to combine multiple services
9. **Setup & Configuration** - Step-by-step setup instructions
10. **Customization & Extension** - How to add new features
11. **Troubleshooting** - Common issues and solutions
12. **Best Practices** - Security, performance, and code quality guidelines

## File Sizes

- **Markdown**: ~24 KB
- **PDF**: ~38 KB
- **Total documentation**: Comprehensive coverage of all aspects

## Notes

- The PDF is automatically opened after generation (on supported systems)
- The document uses professional styling with proper page breaks
- Code examples are properly formatted with syntax highlighting
- Tables and diagrams are included where appropriate 