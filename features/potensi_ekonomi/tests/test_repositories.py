import pytest
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.potensi_ekonomi.repositories import UnitUsahaRepository

pytestmark = pytest.mark.django_db

class TestUnitUsahaRepository:
    def test_list_published_hanya_mengembalikan_yang_aktif(self):
        repo = UnitUsahaRepository()
        
        # Buat 1 Draft, 1 Published
        repo.create_unit({
            "nama_usaha": "Koperasi Draft", 
            "kategori": "KOPERASI", 
            "deskripsi": "Tes", 
            "is_published": False
        })
        repo.create_unit({
            "nama_usaha": "Wisata Aktif", 
            "kategori": "WISATA", 
            "deskripsi": "Tes", 
            "is_published": True
        })

        hasil_published = repo.list_published()
        hasil_semua = repo.list_all()

        assert hasil_semua.count() == 2
        assert hasil_published.count() == 1
        assert hasil_published.first().nama_usaha == "Wisata Aktif"

    def test_update_dan_delete_unit_bekerja_dengan_baik(self):
        repo = UnitUsahaRepository()
        unit = repo.create_unit({"nama_usaha": "Lama", "kategori": "JASA", "deskripsi": ""})
        
        # Test Update
        unit_updated = repo.update_unit(unit, {"nama_usaha": "Baru", "is_published": True})
        assert unit_updated.nama_usaha == "Baru"
        assert unit_updated.is_published is True

        # Test Delete
        repo.delete_unit(unit_updated)
        assert repo.list_all().count() == 0