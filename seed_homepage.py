import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_django.settings')
django.setup()

from faker import Faker
from django.utils import timezone

# Model Imports
from features.auth_warga.models import CustomUser
from features.layanan_administrasi.models import LayananSurat
from features.pengaduan_warga.models import LayananPengaduan
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.publikasi_informasi.models import Publikasi
from features.profil_wilayah.models import WilayahDusun, ProfilDesa, WilayahPerangkat
from features.homepage_konten.models import (
    HomepageContent, 
    HomepageCultureCard, 
    HomepageRecoveryItem,
    HomepagePotentialOpportunityItem,
    HomepageFacility, 
    HomepageGalleryItem,
    HomepageFooterLink,
    HomepageStatisticItem
)

fake = Faker('id_ID')

def seed_users(n=20):
    print(f"Seeding {n} CustomUsers...")
    users = []
    if not CustomUser.objects.filter(role='SUPERADMIN').exists():
        CustomUser.objects.create_superuser(
            nik="1234567890123456",
            password="adminpassword",
            nama_lengkap="Administrator Utama"
        )
    
    # Regular users
    for _ in range(n):
        nik = str(fake.random_number(digits=16, fix_len=True))
        if CustomUser.objects.filter(nik=nik).exists(): continue
        u = CustomUser.objects.create_user(nik=nik, nama_lengkap=fake.name(), password='password123', role='WARGA')
        users.append(u)
    return users

def seed_homepage_konten():
    print("🚀 Seeding Detailed Homepage Content...")
    # 1. Main Content
    hp, created = HomepageContent.objects.get_or_create(
        id=1,
        defaults={
            'village_name': 'Desa Mandian Gajah',
            'tagline': 'Gerbang Digital Menuju Desa Mandiri dan Sejahtera',
            'hero_badge': 'Official Digital Portal',
            'hero_description': 'Selamat datang di pusat layanan mandiri dan informasi publik resmi Desa Mandian Gajah. Kami berkomitmen memberikan pelayanan transparan, cepat, dan efisien bagi seluruh warga melalui teknologi informasi.',
            'hero_image': 'https://images.unsplash.com/photo-1596422846543-75c6fc18a593?q=80&w=1200',
            'brand_logo_url': 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Logo_Kabupaten_Siak.png',
            'brand_logo_alt': 'Logo Kabupaten Siak',
            'brand_region_label': 'Kabupaten Siak, Riau',
            'contact_address': 'Jl. Lintas Desa No. 45, Mandian Gajah, Kec. Minas, Kabupaten Siak, Riau 28664',
            'contact_whatsapp': '6281234567890',
            'contact_map_image': 'https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=1000',
            'quick_stats_description': 'Desa Mandian Gajah mencatatkan pertumbuhan ekonomi dan infrastruktur yang signifikan sebesar 12% di tahun terakhir.',
            'naming_title': 'Asal Usul Mandian Gajah',
            'naming_description': 'Dahulu kala, kawasan di tepian sungai ini merupakan lokasi favorit gajah-gajah liar untuk mandi dan berkumpul. Seiring waktu, para pemukim awal menamai daerah ini Mandian Gajah sebagai penghormatan terhadap alam.',
            'naming_image': 'https://images.unsplash.com/photo-1557008075-7f2c5efa4cfd?q=80&w=800',
            'naming_quote': 'Nama adalah doa, dan Mandian Gajah adalah doa bagi kelestarian alam kami.',
            'culture_title': 'Nilai & Tradisi Kami',
            'culture_description': 'Warisan leluhur yang tetap bernafas dalam harmoni modernitas, menjaga keberagaman dalam satu bingkai kebersamaan.',
            'sialang_title': 'Hutan Sialang Lestari',
            'sialang_description': 'Hutan Sialang kami adalah jantung ekosistem yang menyediakan madu asli dan menjaga cadangan air tanah bagi generasi mendatang.',
            'sialang_image': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1000',
            'sialang_badge': 'Zona Konservasi',
            'sialang_stat': '250+ Spesies Endemik',
            'sialang_quote': 'Hutan adalah ibu, yang memberi nafas bagi setiap makhluk di dalamnya.',
            'peat_title': 'Ekosistem Gambut Sehat',
            'peat_description': 'Kami menjaga lahan gambut agar tetap basah untuk mencegah kebakaran dan menjaga stabilitas iklim mikro desa.',
            'peat_quote': 'Gambut basah, desa aman dari asap dan bencana.',
            'peat_images': [
                'https://images.unsplash.com/photo-1502082553048-f009c37129b9?q=80&w=500',
                'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?q=80&w=500'
            ],
            'recovery_title': 'Pemulihan Ekonomi Pasca Pandemi',
            'recovery_description': 'Melalui pemberdayaan UMKM lokal dan digitalisasi pasar desa, kami bangkit lebih kuat untuk kesejahteraan bersama.',
            'potential_title': 'Potensi Strategis Desa',
            'potential_quote': 'Dari hulu ke hilir, setiap jengkal tanah Mandian Gajah adalah berkah ekonomi yang luar biasa.',
            'potential_opportunities_title': 'Peluang Investasi & Kolaborasi',
            'facilities_title': 'Fasilitas Layanan Utama',
            'gallery_title': 'Galeri Visual Desa',
            'gallery_description': 'Intip keindahan sudut desa dan keceriaan warga kami melalui lensa kamera.',
            'contact_title': 'Hubungi Kami',
            'contact_description': 'Pintu kantor desa selalu terbuka untuk aspirasi dan pelayanan bagi seluruh warga.',
            'footer_description': 'Official Digital Government Platform for Desa Mandian Gajah. Melayani dengan integritas dan inovasi.',
            'footer_copyright': '© 2024 Pemerintah Desa Mandian Gajah. Developed by Digit Village Team.',
            'footer_badges': ['SmartVillage', 'CleanGov', 'OpenData'],
            'office_hours': [
                {'day': 'Senin - Kamis', 'time': '08:00 - 15:30'},
                {'day': 'Jumat', 'time': '08:00 - 11:30'}
            ]
        }
    )

    # Clean existing sub-items to avoid duplicates in re-seeding
    HomepageCultureCard.objects.filter(homepage=hp).delete()
    HomepageRecoveryItem.objects.filter(homepage=hp).delete()
    HomepagePotentialOpportunityItem.objects.filter(homepage=hp).delete()
    HomepageFacility.objects.filter(homepage=hp).delete()
    HomepageGalleryItem.objects.filter(homepage=hp).delete()
    HomepageFooterLink.objects.filter(homepage=hp).delete()
    HomepageStatisticItem.objects.filter(homepage=hp).delete()

    # 2. Culture Cards
    cultures = [
        ('ZapinTradisi', 'Tarian Zapin', 'Warisan Melayu yang tetap hidup di setiap perayaan desa.', 'music'),
        ('AdatLama', 'Musyawarah Desa', 'Keputusan besar selalu lahir dari ruang diskusi yang hangat.', 'users'),
        ('GotongRoyong', 'Tradisi Rewan', 'Membantu tetangga dengan sukarela dalam setiap hajat besar.', 'heart'),
    ]
    for i, (key, title, desc, icon) in enumerate(cultures):
        HomepageCultureCard.objects.create(homepage=hp, title=title, description=desc, icon=icon, sort_order=i)

    # 3. Recovery Items
    recoveries = [
        ('DigitalTrade', 'E-Katalog UMKM', 'Marketplace desa untuk menjangkau pembeli di luar provinsi.', 'shopping-cart'),
        ('AgroInovasi', 'Pertanian Presisi', 'Penggunaan drone untuk memantau kesehatan tanaman padi.', 'zap'),
    ]
    for i, (key, title, desc, icon) in enumerate(recoveries):
        HomepageRecoveryItem.objects.create(homepage=hp, title=title, description=desc, icon=icon, sort_order=i)

    # 4. Potentials
    potentials = [
        ('Tourism', 'Wisata Sungai Gajah', 'Pengembangan kawasan eko-wisata berbasis pelestarian alam.', 'map'),
        ('Energy', 'Pembangkit Biogas', 'Pemanfaatan limbah ternak untuk energi bersih rumah tangga.', 'battery-charging'),
    ]
    for i, (key, title, desc, icon) in enumerate(potentials):
        HomepagePotentialOpportunityItem.objects.create(homepage=hp, title=title, description=desc, icon=icon, sort_order=i)

    # 5. Facilities
    facilities = [
        ('hospital', 'Puskesmas Desa'),
        ('school', 'SD Negeri 01'),
        ('wifi', 'Balai WiFi Gratis'),
        ('truck', 'Logistik BUMDes'),
        ('shield-check', 'Poskamling Digital'),
    ]
    for i, (icon, label) in enumerate(facilities):
        HomepageFacility.objects.create(homepage=hp, icon=icon, label=label, sort_order=i)

    # 6. Gallery
    gallery = [
        ('https://images.unsplash.com/photo-1542332213-9b5a5a3fad35?q=80&w=400', 'Pemandangan Sawah', False, 'Sawah menghijau di pagi hari'),
        ('https://images.unsplash.com/photo-1596422846543-75c6fc18a593?q=80&w=800', 'Kantor Desa', True, 'Gedung utama pusat pelayanan'),
        ('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=400', 'Anak Desa', False, 'Masa depan cerah Mandian Gajah'),
    ]
    for i, (img, alt, tall, cap) in enumerate(gallery):
        HomepageGalleryItem.objects.create(homepage=hp, image=img, alt=alt, tall=tall, caption=cap, sort_order=i)

    # 7. Stats
    stats = [
        ('Luas Wilayah', '1,250 Ha'),
        ('Penduduk', '3,420 Jiwa'),
        ('Anggaran Desa', '1.2 Milyar'),
        ('Penerima BLT', '125 KK'),
    ]
    for i, (label, val) in enumerate(stats):
        HomepageStatisticItem.objects.create(homepage=hp, label=label, value=val, sort_order=i)

    print("✅ Homepage Seed Completed!")

if __name__ == '__main__':
    print("--- RE-SEEDING HOMEPAGE DATA ---")
    try:
        seed_users(5) # Add a few more users
        seed_homepage_konten()
        print("\n🎉 ALL DONE!")
    except Exception as e:
        import traceback
        traceback.print_exc()
