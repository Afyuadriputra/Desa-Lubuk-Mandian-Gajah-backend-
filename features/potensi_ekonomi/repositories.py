# features/potensi_ekonomi/repositories.py

from django.db.models import QuerySet
from features.potensi_ekonomi.models import BumdesUnitUsaha


class UnitUsahaRepository:
    def get_by_id(self, unit_id) -> BumdesUnitUsaha | None:
        return BumdesUnitUsaha.objects.filter(id=unit_id).first()

    def list_published(self) -> QuerySet[BumdesUnitUsaha]:
        return BumdesUnitUsaha.objects.filter(is_published=True)

    def list_all(self) -> QuerySet[BumdesUnitUsaha]:
        return BumdesUnitUsaha.objects.all()

    def create_unit(self, data: dict) -> BumdesUnitUsaha:
        return BumdesUnitUsaha.objects.create(**data)

    def update_unit(self, unit: BumdesUnitUsaha, data: dict) -> BumdesUnitUsaha:
        for field, value in data.items():
            setattr(unit, field, value)
        unit.save()
        return unit
        
    def delete_unit(self, unit: BumdesUnitUsaha) -> None:
        unit.delete()