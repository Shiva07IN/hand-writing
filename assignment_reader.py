"""
MUJ Assignment Agent - Assignment Reader
Extracts text content from PDF and DOCX assignment files.
"""

import re
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
from rich.console import Console

console = Console()


def read_pdf(file_path: Path) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(str(file_path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())
        
        full_text = "\n\n".join(text_parts)
        console.print(f"  [green]✓[/green] Extracted {len(reader.pages)} page(s) from PDF")
        return full_text
    except Exception as e:
        console.print(f"  [red]✗[/red] Error reading PDF: {e}")
        return ""


def read_docx(file_path: Path) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = Document(str(file_path))
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())
        
        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)
        
        full_text = "\n".join(text_parts)
        console.print(f"  [green]✓[/green] Extracted {len(doc.paragraphs)} paragraphs from DOCX")
        return full_text
    except Exception as e:
        console.print(f"  [red]✗[/red] Error reading DOCX: {e}")
        return ""


def read_text(file_path: Path) -> str:
    """Read a plain text file."""
    try:
        text = file_path.read_text(encoding="utf-8")
        console.print(f"  [green]✓[/green] Read text file ({len(text)} characters)")
        return text
    except Exception as e:
        console.print(f"  [red]✗[/red] Error reading text file: {e}")
        return ""


def read_assignment(file_path: str | Path) -> str:
    """
    Read an assignment file and return its text content.
    Supports: .pdf, .docx, .doc, .txt
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        return ""
    
    console.print(f"\n[cyan]📄 Reading:[/cyan] {file_path.name}")
    
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        return read_pdf(file_path)
    elif suffix in (".docx", ".doc"):
        return read_docx(file_path)
    elif suffix in (".txt", ".md"):
        return read_text(file_path)
    else:
        console.print(f"[yellow]Warning:[/yellow] Unsupported file type '{suffix}', trying as text...")
        return read_text(file_path)


def extract_questions(raw_text: str) -> list[str]:
    """
    Attempt to extract individual questions from assignment text.
    Returns a list of question strings.
    """
    if not raw_text.strip():
        return []
    
    # Try common patterns: "Q1.", "Question 1:", "1.", "1)", "(a)", etc.
    patterns = [
        r'(?:Q(?:uestion)?\.?\s*\d+[.:)\s])',  # Q1. or Question 1:
        r'(?:^\s*\d+[.:)\s])',                     # 1. or 1) at line start
        r'(?:^\s*[a-z][.:)\s])',                    # a. or a)
        r'(?:^\s*\([a-z0-9]+\))',                   # (a) or (1)
    ]
    
    combined_pattern = "|".join(patterns)
    
    # Split on question markers
    parts = re.split(f'({combined_pattern})', raw_text, flags=re.MULTILINE | re.IGNORECASE)
    
    questions = []
    current_q = ""
    
    for part in parts:
        if not part:
            continue
        if re.match(combined_pattern, part, re.IGNORECASE):
            if current_q.strip():
                questions.append(current_q.strip())
            current_q = part
        else:
            current_q += part
    
    if current_q.strip():
        questions.append(current_q.strip())
    
    # If no questions were found, return the whole text as one block
    if not questions:
        questions = [raw_text.strip()]
    
    return questions
