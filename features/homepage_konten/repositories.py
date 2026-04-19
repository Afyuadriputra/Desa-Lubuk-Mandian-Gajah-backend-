from django.db import models

from features.homepage_konten.models import (
    HomepageContent,
    HomepageCultureCard,
    HomepageFacility,
    HomepageFooterLink,
    HomepageGalleryItem,
    HomepagePotentialOpportunityItem,
    HomepageRecoveryItem,
    HomepageStatisticItem,
)


CHILD_MODEL_MAP = {
    "culture_cards": HomepageCultureCard,
    "recovery_items": HomepageRecoveryItem,
    "potential_opportunities": HomepagePotentialOpportunityItem,
    "facilities": HomepageFacility,
    "gallery": HomepageGalleryItem,
    "footer_links": HomepageFooterLink,
    "stats_items": HomepageStatisticItem,
}


class HomepageRepository:
    def get_singleton(self) -> HomepageContent:
        content, _ = HomepageContent.objects.get_or_create(id=1)
        return content

    def update_singleton(self, data: dict) -> HomepageContent:
        content = self.get_singleton()
        for field, value in data.items():
            setattr(content, field, value)
        content.save()
        return content

    def get_admin_content(self) -> HomepageContent:
        return (
            HomepageContent.objects.prefetch_related(
                "homepageculturecard_set",
                "homepagerecoveryitem_set",
                "homepagepotentialopportunityitem_set",
                "homepagefacility_set",
                "homepagegalleryitem_set",
                "homepagefooterlink_set",
                "homepagestatisticitem_set",
            )
            .filter(id=1)
            .first()
            or self.get_singleton()
        )

    def list_child_items(self, key: str, homepage: HomepageContent | None = None):
        model = CHILD_MODEL_MAP[key]
        homepage = homepage or self.get_singleton()
        return model.objects.filter(homepage=homepage).order_by("sort_order", "id")

    def get_child_item(self, key: str, item_id: int):
        model = CHILD_MODEL_MAP[key]
        return model.objects.filter(id=item_id).first()

    def create_child_item(self, key: str, data: dict):
        model = CHILD_MODEL_MAP[key]
        return model.objects.create(**data)

    def update_child_item(self, item: models.Model, data: dict):
        for field, value in data.items():
            setattr(item, field, value)
        item.save()
        return item

    def delete_child_item(self, item: models.Model) -> None:
        item.delete()
