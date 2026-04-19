from django.db import models


class HomepageContent(models.Model):
    tagline = models.CharField(max_length=255, blank=True, default="")
    hero_image = models.URLField(blank=True, default="")
    hero_badge = models.CharField(max_length=100, blank=True, default="")
    brand_logo_url = models.URLField(blank=True, default="")
    brand_logo_alt = models.CharField(max_length=150, blank=True, default="")
    brand_region_label = models.CharField(max_length=150, blank=True, default="")
    village_name = models.CharField(max_length=150, blank=True, default="")
    hero_description = models.TextField(blank=True, default="")
    contact_address = models.TextField(blank=True, default="")
    contact_whatsapp = models.CharField(max_length=30, blank=True, default="")
    contact_map_image = models.URLField(blank=True, default="")
    quick_stats_description = models.TextField(blank=True, default="")

    naming_title = models.CharField(max_length=255, blank=True, default="")
    naming_description = models.TextField(blank=True, default="")
    naming_image = models.URLField(blank=True, default="")
    naming_quote = models.TextField(blank=True, default="")

    culture_title = models.CharField(max_length=255, blank=True, default="")
    culture_description = models.TextField(blank=True, default="")

    sialang_title = models.CharField(max_length=255, blank=True, default="")
    sialang_description = models.TextField(blank=True, default="")
    sialang_image = models.URLField(blank=True, default="")
    sialang_badge = models.CharField(max_length=100, blank=True, default="")
    sialang_stat = models.CharField(max_length=120, blank=True, default="")
    sialang_quote = models.TextField(blank=True, default="")

    peat_title = models.CharField(max_length=255, blank=True, default="")
    peat_description = models.TextField(blank=True, default="")
    peat_quote = models.TextField(blank=True, default="")
    peat_images = models.JSONField(default=list, blank=True)

    potential_quote = models.TextField(blank=True, default="")
    facilities_title = models.CharField(max_length=255, blank=True, default="")

    footer_description = models.TextField(blank=True, default="")
    footer_badges = models.JSONField(default=list, blank=True)
    footer_copyright = models.CharField(max_length=255, blank=True, default="")
    office_hours = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "homepage_content"


class SortedHomepageItem(models.Model):
    homepage = models.ForeignKey(HomepageContent, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]


class HomepageCultureCard(SortedHomepageItem):
    icon = models.CharField(max_length=100, blank=True, default="")
    title = models.CharField(max_length=150)
    description = models.TextField()

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_culture_card"


class HomepageRecoveryItem(SortedHomepageItem):
    icon = models.CharField(max_length=100, blank=True, default="")
    title = models.CharField(max_length=150)
    description = models.TextField()
    wrapper = models.CharField(max_length=150, blank=True, default="")

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_recovery_item"


class HomepagePotentialOpportunityItem(SortedHomepageItem):
    icon = models.CharField(max_length=100, blank=True, default="")
    title = models.CharField(max_length=150)
    description = models.TextField()

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_potential_opportunity_item"


class HomepageFacility(SortedHomepageItem):
    icon = models.CharField(max_length=100, blank=True, default="")
    label = models.CharField(max_length=150)

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_facility"


class HomepageGalleryItem(SortedHomepageItem):
    image = models.URLField()
    alt = models.CharField(max_length=150)
    tall = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True, default="")

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_gallery_item"


class HomepageFooterLink(SortedHomepageItem):
    label = models.CharField(max_length=100)
    href = models.CharField(max_length=255)

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_footer_link"


class HomepageStatisticItem(SortedHomepageItem):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta(SortedHomepageItem.Meta):
        db_table = "homepage_statistic_item"
