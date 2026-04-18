# toolbox/pdf_generator/tasks.py (Baru)
from celery import shared_task
from .renderer import generate_pdf_from_html

@shared_task(bind=True, max_retries=3)
def task_generate_dan_simpan_pdf_surat(self, surat_id: str, html_string: str):
    """
    Eksekusi WeasyPrint di background worker.
    """
    try:
        pdf_bytes = generate_pdf_from_html(html_string)
        # Logika menyimpan PDF ke S3/Storage ...
    except Exception as exc:
        self.retry(exc=exc, countdown=10)