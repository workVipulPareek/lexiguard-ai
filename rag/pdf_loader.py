import io
from pypdf import PdfReader


def extract_text_from_pdf(file) -> str:
    """
    Accept a file path (str) or a file-like object (bytes/BytesIO).
    Returns extracted plain text from all pages.
    """
    if isinstance(file, (str, bytes)):
        if isinstance(file, bytes):
            file = io.BytesIO(file)
        reader = PdfReader(file)
    else:
        reader = PdfReader(file)

    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)


def pdf_to_txt(pdf_path: str, txt_path: str) -> str:
    """
    Read a PDF from disk, extract text, write to .txt file.
    Returns the txt_path.
    """
    with open(pdf_path, "rb") as f:
        text = extract_text_from_pdf(f)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return txt_path