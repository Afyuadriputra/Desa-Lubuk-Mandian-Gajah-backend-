# toolbox/pdf_generator/naming.py

from django.utils import timezone

def generate_nomor_surat(jenis_surat: str, unique_id: str) -> str:
    """
    Menghasilkan nomor surat dengan format resmi.
    Contoh: 470/SKU/IV/2026/A1B2
    Kode 470 biasanya adalah klasifikasi administrasi kependudukan.
    """
    now = timezone.now()
    
    # Konversi bulan ke Romawi
    bulan_romawi = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    bulan = bulan_romawi[now.month]
    tahun = now.year
    
    # Ambil 4 karakter pertama dari ID untuk keunikan
    short_id = str(unique_id).split("-")[0][:4].upper()
    
    return f"470/{jenis_surat.upper()}/{bulan}/{tahun}/{short_id}"