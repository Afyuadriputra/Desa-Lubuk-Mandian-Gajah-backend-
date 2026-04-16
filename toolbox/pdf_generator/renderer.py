# toolbox/pdf_generator/renderer.py

import io
from weasyprint import HTML
from toolbox.logging import get_logger

logger = get_logger("toolbox.pdf_generator")

def generate_pdf_from_html(html_string: str, base_url: str | None = None) -> bytes:
    """
    Menghasilkan data byte PDF dari string HTML menggunakan WeasyPrint.
    base_url berguna jika HTML merujuk ke static file lokal (CSS/Images).
    """
    try:
        pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
        return pdf_file
    except Exception as e:
        logger.error("Gagal men-generate PDF: {error}", error=str(e))
        raise RuntimeError(f"Kegagalan internal saat merender PDF: {e}")