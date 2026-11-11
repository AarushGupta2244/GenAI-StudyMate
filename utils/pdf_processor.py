from io import BytesIO
from pypdf import PdfReader

from config import MAX_PDF_PAGES


def extract_pdf_text(uploaded_file):
    """
    Extract text from an uploaded PDF file.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        tuple: (extracted_text, total_pages)
    """

    try:
        pdf_bytes = uploaded_file.getvalue()
        reader = PdfReader(BytesIO(pdf_bytes))

        total_pages = len(reader.pages)

        if total_pages == 0:
            raise ValueError("The uploaded PDF is empty.")

        if total_pages > MAX_PDF_PAGES:
            raise ValueError(
                f"PDF has {total_pages} pages. "
                f"Maximum allowed pages: {MAX_PDF_PAGES}."
            )

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""

            if page_text.strip():
                extracted_pages.append(
                    f"\n--- Page {page_number} ---\n{page_text.strip()}"
                )

        extracted_text = "\n".join(extracted_pages).strip()

        if not extracted_text:
            raise ValueError(
                "No readable text found. This PDF may contain scanned images."
            )

        return extracted_text, total_pages

    except Exception as error:
        raise RuntimeError(
            f"PDF processing failed: {str(error)}"
        ) from error


def split_text_into_chunks(text, chunk_size=6000, overlap=500):
    """
    Split long text into smaller overlapping chunks.
    """

    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # Try to end at a word boundary.
        if end < text_length:
            boundary = text.rfind(" ", start, end)

            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks