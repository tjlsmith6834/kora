import os
import io
import csv
import json
import subprocess
import PyPDF2

def extract_text_from_pdf(pdf_input):
    """
    Extract text from a PDF file.
    If pdf_input is a file-like object, use it directly.
    Otherwise, assume it's a file path.
    """
    if hasattr(pdf_input, "read"):
        pdf_input.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_input)
    else:
        with open(pdf_input, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text() or ""
        text += page_text
    return text

def extract_text_from_csv(csv_input):
    """
    Extract text from a CSV file.
    If csv_input is a file-like object, read and decode it,
    then use io.StringIO to wrap it for csv.reader.
    """
    if hasattr(csv_input, "read"):
        content = csv_input.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        csv_file = io.StringIO(content)
        reader = csv.reader(csv_file)
    else:
        with open(csv_input, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
    lines = []
    for row in reader:
        lines.append(", ".join(row))
    return "\n".join(lines)

def extract_text_from_txt(txt_input):
    """
    Extract text from a TXT file.
    """
    if hasattr(txt_input, "read"):
        content = txt_input.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return content
    else:
        with open(txt_input, 'r', encoding='utf-8') as file:
            return file.read()

def extract_text_from_json(json_input):
    """
    Extract text from a JSON file and pretty-print it.
    """
    if hasattr(json_input, "read"):
        content = json_input.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        json_data = json.loads(content)
    else:
        with open(json_input, "r", encoding='utf-8') as file:
            json_data = json.load(file)
    return json.dumps(json_data, indent=4)

def extract_text_from_doc(doc_input):
    """
    Extract text from a .doc file.
    If given a file-like object, you may need to write its contents
    to a temporary file first (not implemented here).
    """
    if hasattr(doc_input, "read"):
        # Optionally, write to a temporary file here and then process.
        raise NotImplementedError("File-like objects for .doc files are not supported yet.")
    else:
        try:
            if os.name == "nt":  # Windows
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                doc = word.Documents.Open(doc_input)
                text = doc.Content.Text
                doc.Close()
                word.Quit()
                return text.strip()
            else:  # Linux/macOS (requires antiword)
                result = subprocess.run(["antiword", doc_input], capture_output=True, text=True)
                return result.stdout.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from .doc file: {e}")

def extract_text_from_file(file_input):
    """
    Determines the file type (using the file name if available)
    and extracts text accordingly.
    Supported formats: .pdf, .csv, .txt, .json, .doc
    """
    # If file_input is a file-like object, try to use its .name attribute.
    if hasattr(file_input, "name"):
        file_name = file_input.name
    else:
        file_name = file_input

    _, ext = os.path.splitext(file_name)
    extractors = {
        ".pdf": extract_text_from_pdf,
        ".csv": extract_text_from_csv,
        ".txt": extract_text_from_txt,
        ".json": extract_text_from_json,
        ".doc": extract_text_from_doc,
    }
    extractor = extractors.get(ext.lower())
    if extractor:
        return extractor(file_input)
    else:
        raise ValueError(f"Unsupported file format: {ext}")