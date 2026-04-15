# toolbox/storage/paths.py

from django.utils import timezone

from toolbox.storage.media import make_safe_filename


def _date_path() -> str:
    now = timezone.now()
    return f"{now:%Y}/{now:%m}"


def perangkat_photo_upload_path(instance, filename: str) -> str:
    safe_name = make_safe_filename(filename, prefix="perangkat")
    return f"perangkat/{_date_path()}/{safe_name}"


def pengaduan_bukti_upload_path(instance, filename: str) -> str:
    safe_name = make_safe_filename(filename, prefix="pengaduan")
    return f"pengaduan/{_date_path()}/{safe_name}"


def publikasi_media_upload_path(instance, filename: str) -> str:
    safe_name = make_safe_filename(filename, prefix="publikasi")
    return f"publikasi/{_date_path()}/{safe_name}"


def bumdes_media_upload_path(instance, filename: str) -> str:
    safe_name = make_safe_filename(filename, prefix="bumdes")
    return f"bumdes/{_date_path()}/{safe_name}"


def surat_pdf_upload_path(instance, filename: str) -> str:
    safe_name = make_safe_filename(filename, prefix="surat")
    return f"surat/{_date_path()}/{safe_name}"