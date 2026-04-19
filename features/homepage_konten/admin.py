from django.contrib import admin

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


admin.site.register(HomepageContent)
admin.site.register(HomepageCultureCard)
admin.site.register(HomepageRecoveryItem)
admin.site.register(HomepagePotentialOpportunityItem)
admin.site.register(HomepageFacility)
admin.site.register(HomepageGalleryItem)
admin.site.register(HomepageFooterLink)
admin.site.register(HomepageStatisticItem)
