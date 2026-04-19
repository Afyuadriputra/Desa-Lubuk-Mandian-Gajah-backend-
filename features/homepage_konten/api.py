from ninja import Router

from features.homepage_konten.schemas import (
    HomepageAdminContentOut,
    HomepageContentUpdateIn,
    HomepageCultureCardItemIn,
    HomepageCultureCardItemOut,
    HomepageDataOut,
    HomepageFacilityIn,
    HomepageFacilityOut,
    HomepageFooterLinkIn,
    HomepageFooterLinkOut,
    HomepageGalleryItemIn,
    HomepageGalleryItemOut,
    HomepagePotentialOpportunityItemIn,
    HomepagePotentialOpportunityItemOut,
    HomepageRecoveryItemIn,
    HomepageRecoveryItemOut,
    HomepageStatItemIn,
    HomepageStatItemOut,
)
from features.homepage_konten.services import HomepageKontenService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Homepage Konten"])
homepage_service = HomepageKontenService()


@router.get("", auth=None, response={200: HomepageDataOut}, url_name="homepage-public")
def homepage_public_api(request):
    return 200, homepage_service.get_public_homepage()


@router.get("/admin/content", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-content")
def homepage_admin_content_api(request):
    return 200, {"data": HomepageAdminContentOut.model_validate(homepage_service.get_admin_content(request.user)).model_dump(mode="json")}


@router.put("/admin/content", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-content-update")
def homepage_admin_content_update_api(request, payload: HomepageContentUpdateIn):
    data = homepage_service.update_content(request.user, payload.model_dump(mode="python", by_alias=True))
    return 200, {"data": HomepageAdminContentOut.model_validate(data).model_dump(mode="json")}


def _child_response(schema_cls, item):
    return {"data": schema_cls.model_validate(item, from_attributes=True).model_dump(mode="json")}


@router.post("/admin/culture-cards", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-culture-create")
def create_culture_card_api(request, payload: HomepageCultureCardItemIn):
    item = homepage_service.create_child_item(request.user, "culture_cards", payload.model_dump(mode="python"))
    return 201, _child_response(HomepageCultureCardItemOut, item)


@router.put("/admin/culture-cards/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-culture-update")
def update_culture_card_api(request, item_id: int, payload: HomepageCultureCardItemIn):
    item = homepage_service.update_child_item(request.user, "culture_cards", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepageCultureCardItemOut, item)


@router.delete("/admin/culture-cards/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-culture-delete")
def delete_culture_card_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "culture_cards", item_id)
    return {"detail": "Culture card berhasil dihapus."}


@router.post("/admin/recovery-items", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-recovery-create")
def create_recovery_item_api(request, payload: HomepageRecoveryItemIn):
    item = homepage_service.create_child_item(request.user, "recovery_items", payload.model_dump(mode="python"))
    return 201, _child_response(HomepageRecoveryItemOut, item)


@router.put("/admin/recovery-items/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-recovery-update")
def update_recovery_item_api(request, item_id: int, payload: HomepageRecoveryItemIn):
    item = homepage_service.update_child_item(request.user, "recovery_items", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepageRecoveryItemOut, item)


@router.delete("/admin/recovery-items/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-recovery-delete")
def delete_recovery_item_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "recovery_items", item_id)
    return {"detail": "Recovery item berhasil dihapus."}


@router.post("/admin/potential-opportunities", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-opportunity-create")
def create_opportunity_item_api(request, payload: HomepagePotentialOpportunityItemIn):
    item = homepage_service.create_child_item(request.user, "potential_opportunities", payload.model_dump(mode="python"))
    return 201, _child_response(HomepagePotentialOpportunityItemOut, item)


@router.put("/admin/potential-opportunities/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-opportunity-update")
def update_opportunity_item_api(request, item_id: int, payload: HomepagePotentialOpportunityItemIn):
    item = homepage_service.update_child_item(request.user, "potential_opportunities", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepagePotentialOpportunityItemOut, item)


@router.delete("/admin/potential-opportunities/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-opportunity-delete")
def delete_opportunity_item_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "potential_opportunities", item_id)
    return {"detail": "Potential opportunity berhasil dihapus."}


@router.post("/admin/facilities", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-facility-create")
def create_facility_api(request, payload: HomepageFacilityIn):
    item = homepage_service.create_child_item(request.user, "facilities", payload.model_dump(mode="python"))
    return 201, _child_response(HomepageFacilityOut, item)


@router.put("/admin/facilities/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-facility-update")
def update_facility_api(request, item_id: int, payload: HomepageFacilityIn):
    item = homepage_service.update_child_item(request.user, "facilities", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepageFacilityOut, item)


@router.delete("/admin/facilities/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-facility-delete")
def delete_facility_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "facilities", item_id)
    return {"detail": "Facility berhasil dihapus."}


@router.post("/admin/gallery", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-gallery-create")
def create_gallery_item_api(request, payload: HomepageGalleryItemIn):
    item = homepage_service.create_child_item(request.user, "gallery", payload.model_dump(mode="python"))
    return 201, _child_response(HomepageGalleryItemOut, item)


@router.put("/admin/gallery/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-gallery-update")
def update_gallery_item_api(request, item_id: int, payload: HomepageGalleryItemIn):
    item = homepage_service.update_child_item(request.user, "gallery", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepageGalleryItemOut, item)


@router.delete("/admin/gallery/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-gallery-delete")
def delete_gallery_item_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "gallery", item_id)
    return {"detail": "Gallery item berhasil dihapus."}


@router.post("/admin/footer-links", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-footer-link-create")
def create_footer_link_api(request, payload: HomepageFooterLinkIn):
    item = homepage_service.create_child_item(request.user, "footer_links", payload.model_dump(mode="python"))
    return 201, _child_response(HomepageFooterLinkOut, item)


@router.put("/admin/footer-links/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-footer-link-update")
def update_footer_link_api(request, item_id: int, payload: HomepageFooterLinkIn):
    item = homepage_service.update_child_item(request.user, "footer_links", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepageFooterLinkOut, item)


@router.delete("/admin/footer-links/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-footer-link-delete")
def delete_footer_link_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "footer_links", item_id)
    return {"detail": "Footer link berhasil dihapus."}


@router.post("/admin/stats", auth=AuthAdminOnly, response={201: dict}, url_name="homepage-admin-stat-create")
def create_stat_item_api(request, payload: HomepageStatItemIn):
    item = homepage_service.create_child_item(request.user, "stats_items", payload.model_dump(mode="python"))
    return 201, _child_response(HomepageStatItemOut, item)


@router.put("/admin/stats/{item_id}", auth=AuthAdminOnly, response={200: dict}, url_name="homepage-admin-stat-update")
def update_stat_item_api(request, item_id: int, payload: HomepageStatItemIn):
    item = homepage_service.update_child_item(request.user, "stats_items", item_id, payload.model_dump(mode="python"))
    return 200, _child_response(HomepageStatItemOut, item)


@router.delete("/admin/stats/{item_id}", auth=AuthAdminOnly, response=dict, url_name="homepage-admin-stat-delete")
def delete_stat_item_api(request, item_id: int):
    homepage_service.delete_child_item(request.user, "stats_items", item_id)
    return {"detail": "Stat item berhasil dihapus."}
