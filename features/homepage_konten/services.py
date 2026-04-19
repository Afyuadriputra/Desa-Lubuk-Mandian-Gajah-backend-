from features.homepage_konten.domain import (
    HomepageKontenAccessError,
    HomepageKontenNotFoundError,
    validate_json_string_list,
    validate_office_hours,
    validate_required_text,
    validate_sort_order,
)
from features.homepage_konten.permissions import can_manage_homepage_content
from features.homepage_konten.repositories import HomepageRepository
from features.potensi_ekonomi.services import PotensiEkonomiService
from features.profil_wilayah.repositories import DusunRepository, ProfilDesaRepository
from toolbox.logging import audit_event
from toolbox.security.sanitizers import sanitize_plain_text


CHILD_CONFIG = {
    "culture_cards": {"action": "HOMEPAGE_CULTURE_CARD", "title_field": "title"},
    "recovery_items": {"action": "HOMEPAGE_RECOVERY_ITEM", "title_field": "title"},
    "potential_opportunities": {"action": "HOMEPAGE_POTENTIAL_OPPORTUNITY", "title_field": "title"},
    "facilities": {"action": "HOMEPAGE_FACILITY", "title_field": "label"},
    "gallery": {"action": "HOMEPAGE_GALLERY", "title_field": "alt"},
    "footer_links": {"action": "HOMEPAGE_FOOTER_LINK", "title_field": "label"},
    "stats_items": {"action": "HOMEPAGE_STAT_ITEM", "title_field": "label"},
}


class HomepageKontenService:
    def __init__(
        self,
        repo: HomepageRepository | None = None,
        profil_repo: ProfilDesaRepository | None = None,
        dusun_repo: DusunRepository | None = None,
        ekonomi_service: PotensiEkonomiService | None = None,
    ):
        self.repo = repo or HomepageRepository()
        self.profil_repo = profil_repo or ProfilDesaRepository()
        self.dusun_repo = dusun_repo or DusunRepository()
        self.ekonomi_service = ekonomi_service or PotensiEkonomiService()

    def get_public_homepage(self) -> dict:
        content = self.repo.get_admin_content()
        profil = self.profil_repo.get_profil()
        dusun = list(self.dusun_repo.list_all())
        potentials = list(self.ekonomi_service.get_katalog_publik()[:5])

        village_name = content.village_name or "Lubuk Mandian Gajah"
        hero_description = content.hero_description or self._build_default_hero_description(dusun, profil)
        contact_address = content.contact_address or "Alamat desa belum diatur."

        return {
            "villageName": village_name,
            "tagline": content.tagline,
            "heroDescription": hero_description,
            "heroImage": content.hero_image,
            "heroBadge": content.hero_badge,
            "brand": {
                "logoUrl": content.brand_logo_url,
                "logoAlt": content.brand_logo_alt,
                "regionLabel": content.brand_region_label,
            },
            "stats": self._build_stats(dusun, content),
            "quickStatsDescription": content.quick_stats_description,
            "contact": {
                "address": contact_address,
                "whatsapp": content.contact_whatsapp,
                "mapImage": content.contact_map_image,
            },
            "namingTitle": content.naming_title,
            "namingDescription": content.naming_description,
            "namingImage": content.naming_image,
            "namingQuote": content.naming_quote,
            "cultureTitle": content.culture_title,
            "cultureDescription": content.culture_description,
            "cultureCards": self._serialize_items("culture_cards", content),
            "sialangTitle": content.sialang_title,
            "sialangDescription": content.sialang_description,
            "sialangImage": content.sialang_image,
            "sialangBadge": content.sialang_badge,
            "sialangStat": content.sialang_stat,
            "sialangQuote": content.sialang_quote,
            "peatTitle": content.peat_title,
            "peatDescription": content.peat_description,
            "peatQuote": content.peat_quote,
            "peatImages": content.peat_images,
            "recoveryTitle": content.recovery_title,
            "recoveryDescription": content.recovery_description,
            "recoveryItems": self._serialize_items("recovery_items", content),
            "potentialTitle": content.potential_title,
            "potentials": [
                {
                    "title": item.nama_usaha,
                    "image": item.foto_utama.url if item.foto_utama else "",
                }
                for item in potentials
            ],
            "potentialQuote": content.potential_quote,
            "potentialOpportunitiesTitle": content.potential_opportunities_title,
            "potentialOpportunityItems": self._serialize_items("potential_opportunities", content),
            "facilitiesTitle": content.facilities_title,
            "facilities": self._serialize_items("facilities", content),
            "galleryTitle": content.gallery_title,
            "galleryDescription": content.gallery_description,
            "gallery": self._serialize_items("gallery", content),
            "contactTitle": content.contact_title,
            "contactDescription": content.contact_description,
            "footerLinks": self._serialize_items("footer_links", content),
            "footerDescription": content.footer_description,
            "officeHours": content.office_hours,
            "footerBadges": content.footer_badges,
            "footerCopyright": content.footer_copyright,
        }

    def get_admin_content(self, actor) -> dict:
        self._ensure_can_manage(actor)
        data = self.get_public_homepage()
        content = self.repo.get_singleton()
        data["contactAddressSource"] = "homepage_konten" if content.contact_address else "fallback"
        data["villageNameSource"] = "homepage_konten" if content.village_name else "fallback"
        return data

    def update_content(self, actor, payload: dict):
        self._ensure_can_manage(actor)

        update_data = {
            "village_name": validate_required_text(payload.get("villageName"), "villageName", min_length=2),
            "tagline": validate_required_text(payload.get("tagline"), "tagline", min_length=3),
            "hero_description": validate_required_text(payload.get("heroDescription"), "heroDescription", min_length=10),
            "hero_image": validate_required_text(payload.get("heroImage"), "heroImage", min_length=5),
            "hero_badge": validate_required_text(payload.get("heroBadge"), "heroBadge", min_length=2),
            "brand_logo_url": validate_required_text(payload.get("brand", {}).get("logoUrl"), "brand.logoUrl", min_length=5),
            "brand_logo_alt": validate_required_text(payload.get("brand", {}).get("logoAlt"), "brand.logoAlt", min_length=2),
            "brand_region_label": validate_required_text(payload.get("brand", {}).get("regionLabel"), "brand.regionLabel", min_length=2),
            "contact_address": validate_required_text(payload.get("contact", {}).get("address"), "contact.address", min_length=5),
            "contact_whatsapp": validate_required_text(payload.get("contact", {}).get("whatsapp"), "contact.whatsapp", min_length=5),
            "contact_map_image": validate_required_text(payload.get("contact", {}).get("mapImage"), "contact.mapImage", min_length=5),
            "quick_stats_description": validate_required_text(payload.get("quickStatsDescription"), "quickStatsDescription", min_length=10),
            "naming_title": validate_required_text(payload.get("namingTitle"), "namingTitle", min_length=3),
            "naming_description": validate_required_text(payload.get("namingDescription"), "namingDescription", min_length=10),
            "naming_image": validate_required_text(payload.get("namingImage"), "namingImage", min_length=5),
            "naming_quote": validate_required_text(payload.get("namingQuote"), "namingQuote", min_length=3),
            "culture_title": validate_required_text(payload.get("cultureTitle"), "cultureTitle", min_length=3),
            "culture_description": validate_required_text(payload.get("cultureDescription"), "cultureDescription", min_length=10),
            "sialang_title": validate_required_text(payload.get("sialangTitle"), "sialangTitle", min_length=3),
            "sialang_description": validate_required_text(payload.get("sialangDescription"), "sialangDescription", min_length=10),
            "sialang_image": validate_required_text(payload.get("sialangImage"), "sialangImage", min_length=5),
            "sialang_badge": validate_required_text(payload.get("sialangBadge"), "sialangBadge", min_length=2),
            "sialang_stat": validate_required_text(payload.get("sialangStat"), "sialangStat", min_length=2),
            "sialang_quote": validate_required_text(payload.get("sialangQuote"), "sialangQuote", min_length=3),
            "peat_title": validate_required_text(payload.get("peatTitle"), "peatTitle", min_length=3),
            "peat_description": validate_required_text(payload.get("peatDescription"), "peatDescription", min_length=10),
            "peat_quote": validate_required_text(payload.get("peatQuote"), "peatQuote", min_length=3),
            "peat_images": validate_json_string_list(payload.get("peatImages"), "peatImages"),
            "recovery_title": validate_required_text(payload.get("recoveryTitle"), "recoveryTitle", min_length=3),
            "recovery_description": validate_required_text(payload.get("recoveryDescription"), "recoveryDescription", min_length=10),
            "potential_title": validate_required_text(payload.get("potentialTitle"), "potentialTitle", min_length=3),
            "potential_quote": validate_required_text(payload.get("potentialQuote"), "potentialQuote", min_length=3),
            "potential_opportunities_title": validate_required_text(payload.get("potentialOpportunitiesTitle"), "potentialOpportunitiesTitle", min_length=3),
            "facilities_title": validate_required_text(payload.get("facilitiesTitle"), "facilitiesTitle", min_length=3),
            "gallery_title": validate_required_text(payload.get("galleryTitle"), "galleryTitle", min_length=3),
            "gallery_description": validate_required_text(payload.get("galleryDescription"), "galleryDescription", min_length=10),
            "contact_title": validate_required_text(payload.get("contactTitle"), "contactTitle", min_length=3),
            "contact_description": validate_required_text(payload.get("contactDescription"), "contactDescription", min_length=10),
            "footer_description": validate_required_text(payload.get("footerDescription"), "footerDescription", min_length=10),
            "footer_badges": validate_json_string_list(payload.get("footerBadges"), "footerBadges"),
            "footer_copyright": validate_required_text(payload.get("footerCopyright"), "footerCopyright", min_length=3),
            "office_hours": validate_office_hours(payload.get("officeHours")),
        }

        content = self.repo.update_singleton(update_data)
        audit_event("HOMEPAGE_CONTENT_UPDATED", actor_id=actor.id, target_id=content.id, metadata={})
        return self.get_admin_content(actor)

    def create_child_item(self, actor, key: str, payload: dict):
        self._ensure_can_manage(actor)
        data = self._normalize_child_payload(key, payload)
        data["homepage"] = self.repo.get_singleton()
        item = self.repo.create_child_item(key, data)
        self._audit_child("CREATED", key, actor.id, item.id, data)
        return item

    def update_child_item(self, actor, key: str, item_id: int, payload: dict):
        self._ensure_can_manage(actor)
        item = self.repo.get_child_item(key, item_id)
        if not item:
            raise HomepageKontenNotFoundError("Item homepage tidak ditemukan.")
        data = self._normalize_child_payload(key, payload)
        updated = self.repo.update_child_item(item, data)
        self._audit_child("UPDATED", key, actor.id, updated.id, data)
        return updated

    def delete_child_item(self, actor, key: str, item_id: int) -> None:
        self._ensure_can_manage(actor)
        item = self.repo.get_child_item(key, item_id)
        if not item:
            raise HomepageKontenNotFoundError("Item homepage tidak ditemukan.")
        self.repo.delete_child_item(item)
        self._audit_child("DELETED", key, actor.id, item_id, {})

    def _ensure_can_manage(self, actor) -> None:
        if not can_manage_homepage_content(actor):
            raise HomepageKontenAccessError("Anda tidak memiliki izin mengelola konten homepage.")

    def _normalize_child_payload(self, key: str, payload: dict) -> dict:
        base = {"sort_order": validate_sort_order(payload.get("sort_order", 0))}
        if key == "culture_cards":
            base.update(
                {
                    "icon": sanitize_plain_text(payload.get("icon")),
                    "title": validate_required_text(payload.get("title"), "title"),
                    "description": validate_required_text(payload.get("description"), "description", min_length=5),
                }
            )
        elif key == "recovery_items":
            base.update(
                {
                    "icon": sanitize_plain_text(payload.get("icon")),
                    "title": validate_required_text(payload.get("title"), "title"),
                    "description": validate_required_text(payload.get("description"), "description", min_length=5),
                    "wrapper": sanitize_plain_text(payload.get("wrapper")),
                }
            )
        elif key == "potential_opportunities":
            base.update(
                {
                    "icon": sanitize_plain_text(payload.get("icon")),
                    "title": validate_required_text(payload.get("title"), "title"),
                    "description": validate_required_text(payload.get("description"), "description", min_length=5),
                }
            )
        elif key == "facilities":
            base.update(
                {
                    "icon": sanitize_plain_text(payload.get("icon")),
                    "label": validate_required_text(payload.get("label"), "label"),
                }
            )
        elif key == "gallery":
            base.update(
                {
                    "image": validate_required_text(payload.get("image"), "image", min_length=5),
                    "alt": validate_required_text(payload.get("alt"), "alt", min_length=2),
                    "tall": bool(payload.get("tall", False)),
                    "caption": sanitize_plain_text(payload.get("caption")),
                }
            )
        elif key == "footer_links":
            base.update(
                {
                    "label": validate_required_text(payload.get("label"), "label"),
                    "href": validate_required_text(payload.get("href"), "href", min_length=1),
                }
            )
        elif key == "stats_items":
            base.update(
                {
                    "label": validate_required_text(payload.get("label"), "label", min_length=2),
                    "value": validate_required_text(payload.get("value"), "value", min_length=1),
                }
            )
        return base

    def _build_stats(self, dusun: list, content) -> list[dict]:
        manual_items = [
            {
                "value": item.value,
                "label": item.label,
            }
            for item in self.repo.list_child_items("stats_items", content)
            if item.label.strip().lower() != "dusun"
        ]
        return [{"value": str(len(dusun)), "label": "Dusun"}, *manual_items]

    def _build_default_hero_description(self, dusun: list, profil) -> str:
        if getattr(profil, "sejarah", "").strip():
            return sanitize_plain_text(profil.sejarah)
        if dusun:
            return f"Desa ini memiliki {len(dusun)} dusun yang tercatat di sistem."
        return "Profil singkat desa belum diatur."

    def _serialize_items(self, key: str, content) -> list[dict]:
        items = self.repo.list_child_items(key, content)
        if key == "culture_cards":
            return [
                {
                    "id": item.id,
                    "icon": item.icon,
                    "title": item.title,
                    "description": item.description,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        if key == "recovery_items":
            return [
                {
                    "id": item.id,
                    "icon": item.icon,
                    "title": item.title,
                    "description": item.description,
                    "wrapper": item.wrapper,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        if key == "potential_opportunities":
            return [
                {
                    "id": item.id,
                    "icon": item.icon,
                    "title": item.title,
                    "description": item.description,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        if key == "facilities":
            return [
                {
                    "id": item.id,
                    "icon": item.icon,
                    "label": item.label,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        if key == "gallery":
            return [
                {
                    "id": item.id,
                    "image": item.image,
                    "alt": item.alt,
                    "tall": item.tall,
                    "caption": item.caption,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        if key == "footer_links":
            return [
                {
                    "id": item.id,
                    "label": item.label,
                    "href": item.href,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        if key == "stats_items":
            return [
                {
                    "id": item.id,
                    "label": item.label,
                    "value": item.value,
                    "sort_order": item.sort_order,
                }
                for item in items
            ]
        return []

    def _audit_child(self, suffix: str, key: str, actor_id, target_id, data: dict) -> None:
        config = CHILD_CONFIG[key]
        metadata = {}
        title_field = config["title_field"]
        if title_field in data:
            metadata[title_field] = data[title_field]
        audit_event(f"{config['action']}_{suffix}", actor_id=actor_id, target_id=target_id, metadata=metadata)
