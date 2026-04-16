# toolbox/pdf_generator/templates.py

from django.template.loader import render_to_string

def render_surat_html(template_name: str, context: dict) -> str:
    """
    Merender template Django HTML dengan data context menjadi string.
    Contoh template_name: "pdf_templates/surat_keterangan_usaha.html"
    """
    return render_to_string(template_name, context)