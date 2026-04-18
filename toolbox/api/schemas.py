from ninja import Schema
from toolbox.security.sanitizers import SafeHTMLString, SafePlainTextString

class PublikasiCreateSchema(Schema):
    judul: SafePlainTextString
    konten_html: SafeHTMLString  # <--- Otomatis dibersihkan dari XSS
    jenis: str