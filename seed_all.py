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
    HomepageGalleryItem,
    HomepageStatisticItem,
    HomepageFacility
)

fake = Faker('id_ID')

def seed_users(n=20):
    print(f"Seeding {n} CustomUsers...")
    users = []
    # Ensure one superadmin
    if not CustomUser.objects.filter(role='SUPERADMIN').exists():
        admin = CustomUser.objects.create_superuser(
            nik="1234567890123456",
            password="adminpassword",
            nama_lengkap="Administrator Utama"
        )
        users.append(admin)

    # Regular users
    for _ in range(n):
        nik = str(fake.random_number(digits=16, fix_len=True))
        if CustomUser.objects.filter(nik=nik).exists():
            continue
        u = CustomUser.objects.create_user(
            nik=nik,
            nama_lengkap=fake.name(),
            password='password123',
            nomor_hp=fake.phone_number()[:15],
            role='WARGA'
        )
        users.append(u)
    return users

def seed_wilayah_dusun():
    print("Seeding WilayahDusun...")
    dusun_names = ['Dusun I Barokah', 'Dusun II Makmur', 'Dusun III Sejahtera']
    for name in dusun_names:
        WilayahDusun.objects.get_or_create(
            nama_dusun=name,
            defaults={'kepala_dusun': fake.name()}
        )

def seed_surat(users, n=30):
    print(f"Seeding {n} LayananSurat...")
    jenis_choices = ['SKU', 'SKTM', 'DOMISILI']
    status_choices = ['PENDING', 'VERIFIED', 'PROCESSED', 'DONE', 'REJECTED']
    
    for _ in range(n):
        status = random.choice(status_choices)
        pemohon = random.choice(users)
        LayananSurat.objects.create(
            pemohon=pemohon,
            jenis_surat=random.choice(jenis_choices),
            keperluan=fake.sentence(nb_words=12),
            status=status,
            nomor_surat=f"470/{fake.random_int(min=100, max=999)}/2024" if status == 'DONE' else None
        )

def seed_pengaduan(users, n=20):
    print(f"Seeding {n} LayananPengaduan...")
    kategori_choices = ['Infrastruktur', 'Kesehatan', 'Pendidikan', 'Keamanan']
    status_choices = ['OPEN', 'TRIAGED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
    
    for _ in range(n):
        pelapor = random.choice(users)
        LayananPengaduan.objects.create(
            pelapor=pelapor,
            kategori=random.choice(kategori_choices),
            judul=fake.sentence(nb_words=6),
            deskripsi=fake.paragraph(),
            status=random.choice(status_choices)
        )

def seed_potensi(n=8):
    print(f"Seeding {n} BumdesUnitUsaha...")
    kategori_choices = ['WISATA', 'UMKM', 'JASA', 'PERDAGANGAN']
    for _ in range(n):
        BumdesUnitUsaha.objects.create(
            nama_usaha=fake.company(),
            kategori=random.choice(kategori_choices),
            deskripsi=fake.text(),
            kontak_wa=fake.phone_number()[:15],
            is_published=True
        )

def seed_publikasi(users, n=15):
    print(f"Seeding {n} Publikasi...")
    jenis_choices = ['BERITA', 'PENGUMUMAN']
    for _ in range(n):
        Publikasi.objects.create(
            judul=fake.sentence(nb_words=10),
            jenis=random.choice(jenis_choices),
            konten_html=fake.text(max_nb_chars=3000),
            penulis=random.choice(users),
            status='PUBLISHED',
            published_at=timezone.now() - timedelta(days=random.randint(0, 30))
        )

def seed_homepage():
    print("Seeding HomepageContent & Items...")
    hp, _ = HomepageContent.objects.get_or_create(
        id=1,
        defaults={
            'village_name': 'Mandian Gajah',
            'tagline': 'Bersatu dalam Keberagaman, Maju dalam Digitalisasi',
            'hero_description': 'Layanan mandiri warga untuk pengajuan surat dan pengaduan pembangunan desa secara transparan.',
            'hero_badge': 'Smart Village Portal',
            'footer_copyright': '© 2024 Pemerintah Desa Mandian Gajah'
        }
    )
    
    # Sub items
    if not HomepageCultureCard.objects.filter(homepage=hp).exists():
        HomepageCultureCard.objects.create(homepage=hp, title="Adat Istiadat", description=fake.sentence(), sort_order=1)
        HomepageCultureCard.objects.create(homepage=hp, title="Kearifan Lokal", description=fake.sentence(), sort_order=2)
    
    if not HomepageStatisticItem.objects.filter(homepage=hp).exists():
        HomepageStatisticItem.objects.create(homepage=hp, label="Penduduk", value="2,450", sort_order=1)
        HomepageStatisticItem.objects.create(homepage=hp, label="Luas Wilayah", value="150 Ha", sort_order=2)
        HomepageStatisticItem.objects.create(homepage=hp, label="RT/RW", value="12/4", sort_order=3)

    if not HomepageFacility.objects.filter(homepage=hp).exists():
        HomepageFacility.objects.create(homepage=hp, label="Puskesdes", icon="hospital", sort_order=1)
        HomepageFacility.objects.create(homepage=hp, label="Pasar Desa", icon="shopping-bag", sort_order=2)

if __name__ == '__main__':
    print("--- COMPREHENSIVE SEEDER ---")
    try:
        users = seed_users(20)
        seed_wilayah_dusun()
        seed_surat(users, 30)
        seed_pengaduan(users, 20)
        seed_potensi(10)
        seed_publikasi(users, 15)
        seed_homepage()
        print("\n✅ DATA SEED SUCCESSFUL!")
    except Exception as e:
        import traceback
        traceback.print_exc()
