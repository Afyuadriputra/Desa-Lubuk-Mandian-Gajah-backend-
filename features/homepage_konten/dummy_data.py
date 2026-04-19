from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from faker import Faker


fake = Faker("id_ID")
fake.seed_instance(20260419)


def build_homepage_content_defaults() -> dict[str, Any]:
    return {
        "village_name": "Desa Segamai",
        "tagline": "Lestari di tepian gambut, tumbuh dari sejarah dan gotong royong.",
        "hero_description": (
            "Desa Segamai menghadirkan lanskap gambut, tradisi lokal, dan potensi ekonomi "
            "yang tumbuh dari kerja bersama masyarakat."
        ),
        "hero_image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80",
        "hero_badge": "Profil Desa",
        "brand_logo_url": "https://upload.wikimedia.org/wikipedia/commons/6/68/Coat_of_arms_of_Riau.svg",
        "brand_logo_alt": "Lambang Provinsi Riau",
        "brand_region_label": "Kabupaten Bengkalis, Riau",
        "contact_address": "Jl. Raya Segamai No. 1, Kecamatan Bandar Laksamana, Bengkalis, Riau",
        "contact_whatsapp": "+62 812-3456-7890",
        "contact_map_image": "https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&w=1200&q=80",
        "quick_stats_description": (
            "Gambaran singkat desa untuk mengenal skala wilayah, kehidupan warga, dan arah "
            "pengembangan yang sedang dijalankan."
        ),
        "naming_title": "Asal Nama Segamai",
        "naming_description": (
            "Nama Segamai lahir dari ingatan kolektif warga terhadap ruang hidup, aliran air, "
            "dan jejak hubungan panjang masyarakat dengan wilayah pesisir gambut."
        ),
        "naming_image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1000&q=80",
        "naming_quote": "Nama desa adalah penanda ingatan kolektif masyarakat.",
        "culture_title": "Budaya dan Identitas",
        "culture_description": (
            "Tradisi yang hidup membentuk cara warga menjaga hubungan dengan alam, tetangga, "
            "dan ruang bersama di desa."
        ),
        "sialang_title": "Pohon Sialang dan Pengetahuan Lokal",
        "sialang_description": (
            "Sialang menjadi simbol hubungan harmonis antara manusia, lebah, dan hutan yang "
            "dijaga lintas generasi."
        ),
        "sialang_image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "sialang_badge": "Warisan Ekologis",
        "sialang_stat": "Sumber madu dan pengetahuan lokal",
        "sialang_quote": "Hutan bukan hanya ruang hidup, tetapi juga guru bagi masyarakat.",
        "peat_title": "Bentang Gambut Desa",
        "peat_description": (
            "Ekosistem gambut desa berperan menjaga air, biodiversitas, dan ketahanan wilayah "
            "terhadap musim kering."
        ),
        "peat_quote": "Gambut yang sehat adalah fondasi masa depan desa.",
        "peat_images": [
            "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=900&q=80",
        ],
        "recovery_title": "Upaya Pemulihan dan Perawatan",
        "recovery_description": (
            "Berbagai langkah dilakukan untuk menjaga fungsi ekologis wilayah sambil membuka "
            "ruang ekonomi yang tetap bertanggung jawab."
        ),
        "potential_title": "Potensi Desa",
        "potential_quote": "Potensi lokal tumbuh dari pengetahuan warga dan lanskap yang dijaga.",
        "potential_opportunities_title": "Peluang Pengembangan",
        "facilities_title": "Fasilitas Desa",
        "gallery_title": "Galeri Desa",
        "gallery_description": "Dokumentasi suasana, kegiatan, dan lanskap desa yang hidup.",
        "contact_title": "Kontak dan Lokasi",
        "contact_description": (
            "Hubungi kantor desa untuk layanan, informasi, koordinasi kegiatan, dan kebutuhan "
            "kunjungan lapangan."
        ),
        "footer_description": (
            "Desa yang bertumbuh dengan menjaga identitas, lingkungan, dan masa depan bersama."
        ),
        "footer_badges": ["Gotong Royong", "Lestari", "Berdaya"],
        "footer_copyright": "© 2026 Desa Segamai. Semua hak dilindungi.",
        "office_hours": [
            {"day": "Senin", "time": "08.00 - 16.00"},
            {"day": "Selasa", "time": "08.00 - 16.00"},
            {"day": "Rabu", "time": "08.00 - 16.00"},
            {"day": "Kamis", "time": "08.00 - 16.00"},
            {"day": "Jumat", "time": "08.00 - 11.30", "danger": True},
        ],
    }


def build_culture_cards() -> list[dict[str, Any]]:
    return [
        {
            "icon": "groups",
            "title": "Gotong Royong",
            "description": "Kerja bersama tetap menjadi dasar kegiatan sosial dan pembangunan desa.",
            "sort_order": 1,
        },
        {
            "icon": "record_voice_over",
            "title": "Tradisi Lisan",
            "description": "Cerita turun-temurun menjadi penanda sejarah dan identitas lokal.",
            "sort_order": 2,
        },
        {
            "icon": "handshake",
            "title": "Musyawarah Warga",
            "description": "Keputusan penting lahir dari ruang dialog yang terbuka dan kolektif.",
            "sort_order": 3,
        },
    ]


def build_recovery_items() -> list[dict[str, Any]]:
    return [
        {
            "icon": "recycling",
            "title": "Restorasi Bertahap",
            "description": "Pemulihan area terdampak dilakukan bertahap dengan pemantauan rutin.",
            "sort_order": 1,
        },
        {
            "icon": "water",
            "title": "Pengelolaan Tata Air",
            "description": "Pengaturan air membantu menjaga kelembapan gambut dan mengurangi risiko kebakaran.",
            "sort_order": 2,
        },
        {
            "icon": "groups",
            "title": "Partisipasi Warga",
            "description": "Warga dilibatkan dalam pemeliharaan, edukasi, dan pengawasan lingkungan.",
            "sort_order": 3,
        },
    ]


def build_potential_opportunities() -> list[dict[str, Any]]:
    return [
        {
            "icon": "storefront",
            "title": "UMKM Lokal",
            "description": "Produk warga dapat diperluas melalui branding, kemasan, dan distribusi digital.",
            "sort_order": 1,
        },
        {
            "icon": "travel_explore",
            "title": "Ekowisata",
            "description": "Wisata berbasis alam dan edukasi lingkungan punya ruang tumbuh yang kuat.",
            "sort_order": 2,
        },
        {
            "icon": "handshake",
            "title": "Kemitraan Desa",
            "description": "Kolaborasi dengan komunitas, kampus, dan pelaku usaha membuka peluang baru.",
            "sort_order": 3,
        },
    ]


def build_facilities() -> list[dict[str, Any]]:
    return [
        {"icon": "account_balance", "label": "Kantor Desa", "sort_order": 1},
        {"icon": "school", "label": "Sekolah", "sort_order": 2},
        {"icon": "health_and_safety", "label": "Layanan Kesehatan", "sort_order": 3},
        {"icon": "construction", "label": "Infrastruktur Jalan", "sort_order": 4},
        {"icon": "water", "label": "Sarana Air Bersih", "sort_order": 5},
    ]


def build_gallery_items() -> list[dict[str, Any]]:
    return [
        {
            "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=80",
            "alt": "Kegiatan warga desa",
            "caption": "Gotong royong warga",
            "tall": True,
            "sort_order": 1,
        },
        {
            "image": "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=80",
            "alt": "Lanskap gambut desa",
            "caption": "Bentang gambut",
            "tall": False,
            "sort_order": 2,
        },
        {
            "image": "https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=900&q=80",
            "alt": "Kantor desa",
            "caption": "Pusat layanan desa",
            "tall": False,
            "sort_order": 3,
        },
        {
            "image": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?auto=format&fit=crop&w=900&q=80",
            "alt": "Aktivitas ekonomi warga",
            "caption": "Produk lokal desa",
            "tall": True,
            "sort_order": 4,
        },
    ]


def build_footer_links() -> list[dict[str, Any]]:
    return [
        {"label": "Beranda", "href": "/homepage", "sort_order": 1},
        {"label": "Sejarah", "href": "/sejarah", "sort_order": 2},
        {"label": "Gambut", "href": "/gambut", "sort_order": 3},
        {"label": "Potensi", "href": "/potensi", "sort_order": 4},
    ]


def build_stats_items() -> list[dict[str, Any]]:
    return [
        {"label": "RW", "value": "4", "sort_order": 1},
        {"label": "RT", "value": "12", "sort_order": 2},
        {"label": "Jiwa", "value": "1.240", "sort_order": 3},
        {"label": "KK", "value": "315", "sort_order": 4},
        {"label": "Ha Gambut", "value": "780", "sort_order": 5},
        {"label": "Embung", "value": "2", "sort_order": 6},
    ]


@dataclass(frozen=True)
class DummyPotential:
    nama_usaha: str
    kategori: str
    deskripsi: str
    kontak_wa: str
    file_stub: str


def build_dummy_potentials() -> list[DummyPotential]:
    categories = ["PERDAGANGAN", "JASA", "WISATA", "UMKM", "JASA"]
    names = ["Madu Hutan Segamai", "Kebun Produktif", "Wisata Susur Desa", "Kerajinan Warga", "Perikanan Lokal"]
    stubs = ["madu-hutan", "kebun-produktif", "wisata-susur", "kerajinan-warga", "perikanan-lokal"]

    items: list[DummyPotential] = []
    for index, name in enumerate(names):
        items.append(
            DummyPotential(
                nama_usaha=name,
                kategori=categories[index],
                deskripsi=fake.paragraph(nb_sentences=3),
                kontak_wa=f"+62 812-3456-78{90 + index}",
                file_stub=stubs[index],
            )
        )
    return items


def build_dummy_dusun_names() -> list[str]:
    return ["Dusun Timur", "Dusun Barat", "Dusun Tengah", "Dusun Pesisir"]
