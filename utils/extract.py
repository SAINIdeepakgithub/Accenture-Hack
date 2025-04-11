from PyPDF2 import PdfReader
import docx2txt
import os

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

def extract_text_from_docx(file):
    with open("temp_resume.docx", "wb") as f:
        f.write(file.read())
    text = docx2txt.process("temp_resume.docx")
    os.remove("temp_resume.docx")
    return text
