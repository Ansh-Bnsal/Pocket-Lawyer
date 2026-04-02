"""
Pocket Lawyer 2.0 — File Service
Text extraction from PDF, DOCX, and plain text files.
"""
import os

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(file_path):
    """Extract text content from a file based on its extension."""
    if not os.path.exists(file_path):
        return ''

    ext = file_path.rsplit('.', 1)[-1].lower()

    if ext == 'txt':
        return _extract_txt(file_path)
    elif ext == 'pdf':
        return _extract_pdf(file_path)
    elif ext in ('doc', 'docx'):
        return _extract_docx(file_path)
    else:
        return ''


def _extract_txt(file_path):
    """Extract text from a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f'[Text extraction failed: {str(e)}]'


def _extract_pdf(file_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return '\n'.join(text_parts)
    except ImportError:
        return '[PDF extraction requires PyPDF2. Install with: pip install PyPDF2]'
    except Exception as e:
        return f'[PDF extraction failed: {str(e)}]'


def _extract_docx(file_path):
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    except ImportError:
        return '[DOCX extraction requires python-docx. Install with: pip install python-docx]'
    except Exception as e:
        return f'[DOCX extraction failed: {str(e)}]'
