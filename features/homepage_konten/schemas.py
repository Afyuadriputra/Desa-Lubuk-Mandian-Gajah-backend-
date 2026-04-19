from typing import Optional

from ninja import Field, Schema

class HomepageBrandOut(Schema):
    logoUrl: str
    logoAlt: str
    regionLabel: str


class HomepageContactOut(Schema):
    address: str
    whatsapp: str
    mapImage: str


class HomepageStatOut(Schema):
    value: str
    label: str


class HomepageStatItemIn(Schema):
    label: str
    value: str
    sort_order: int = 0


class HomepageStatItemOut(Schema):
    id: int
    label: str
    value: str
    sort_order: int


class HomepageCultureCardItemIn(Schema):
    icon: Optional[str] = ""
    title: str
    description: str
    sort_order: int = 0


class HomepageCultureCardItemOut(Schema):
    id: int
    icon: str
    title: str
    description: str
    sort_order: int


class HomepageRecoveryItemIn(Schema):
    icon: Optional[str] = ""
    title: str
    description: str
    wrapper: Optional[str] = ""
    sort_order: int = 0


class HomepageRecoveryItemOut(Schema):
    id: int
    icon: str
    title: str
    description: str
    wrapper: str
    sort_order: int


class HomepagePotentialOpportunityItemIn(Schema):
    icon: Optional[str] = ""
    title: str
    description: str
    sort_order: int = 0


class HomepagePotentialOpportunityItemOut(Schema):
    id: int
    icon: str
    title: str
    description: str
    sort_order: int


class HomepageFacilityIn(Schema):
    icon: Optional[str] = ""
    label: str
    sort_order: int = 0


class HomepageFacilityOut(Schema):
    id: int
    icon: str
    label: str
    sort_order: int


class HomepageGalleryItemIn(Schema):
    image: str
    alt: str
    tall: bool = False
    caption: Optional[str] = ""
    sort_order: int = 0


class HomepageGalleryItemOut(Schema):
    id: int
    image: str
    alt: str
    tall: bool
    caption: str
    sort_order: int


class HomepageFooterLinkIn(Schema):
    label: str
    href: str
    sort_order: int = 0


class HomepageFooterLinkOut(Schema):
    id: int
    label: str
    href: str
    sort_order: int


class HomepageOfficeHourIn(Schema):
    day: str
    time: str
    danger: bool = False


class HomepageOfficeHourOut(Schema):
    day: str
    time: str
    danger: bool = False


class HomepageContentUpdateIn(Schema):
    villageName: str = Field(..., alias="villageName")
    tagline: str
    heroDescription: str = Field(..., alias="heroDescription")
    heroImage: str = Field(..., alias="heroImage")
    heroBadge: str = Field(..., alias="heroBadge")
    brand: HomepageBrandOut
    quickStatsDescription: str = Field(..., alias="quickStatsDescription")
    contact: HomepageContactOut
    namingTitle: str = Field(..., alias="namingTitle")
    namingDescription: str = Field(..., alias="namingDescription")
    namingImage: str = Field(..., alias="namingImage")
    namingQuote: str = Field(..., alias="namingQuote")
    cultureTitle: str = Field(..., alias="cultureTitle")
    cultureDescription: str = Field(..., alias="cultureDescription")
    sialangTitle: str = Field(..., alias="sialangTitle")
    sialangDescription: str = Field(..., alias="sialangDescription")
    sialangImage: str = Field(..., alias="sialangImage")
    sialangBadge: str = Field(..., alias="sialangBadge")
    sialangStat: str = Field(..., alias="sialangStat")
    sialangQuote: str = Field(..., alias="sialangQuote")
    peatTitle: str = Field(..., alias="peatTitle")
    peatDescription: str = Field(..., alias="peatDescription")
    peatQuote: str = Field(..., alias="peatQuote")
    peatImages: list[str] = Field(default_factory=list, alias="peatImages")
    recoveryTitle: str = Field(..., alias="recoveryTitle")
    recoveryDescription: str = Field(..., alias="recoveryDescription")
    potentialTitle: str = Field(..., alias="potentialTitle")
    potentialQuote: str = Field(..., alias="potentialQuote")
    potentialOpportunitiesTitle: str = Field(..., alias="potentialOpportunitiesTitle")
    facilitiesTitle: str = Field(..., alias="facilitiesTitle")
    galleryTitle: str = Field(..., alias="galleryTitle")
    galleryDescription: str = Field(..., alias="galleryDescription")
    contactTitle: str = Field(..., alias="contactTitle")
    contactDescription: str = Field(..., alias="contactDescription")
    footerDescription: str = Field(..., alias="footerDescription")
    footerBadges: list[str] = Field(default_factory=list, alias="footerBadges")
    footerCopyright: str = Field(..., alias="footerCopyright")
    officeHours: list[HomepageOfficeHourIn] = Field(default_factory=list, alias="officeHours")


class HomepagePotentialOut(Schema):
    title: str
    image: str


class HomepageDataOut(Schema):
    villageName: str
    tagline: str
    heroDescription: str
    heroImage: str
    heroBadge: str
    brand: HomepageBrandOut
    stats: list[HomepageStatOut]
    quickStatsDescription: str
    contact: HomepageContactOut
    namingTitle: str
    namingDescription: str
    namingImage: str
    namingQuote: str
    cultureTitle: str
    cultureDescription: str
    cultureCards: list[HomepageCultureCardItemOut]
    sialangTitle: str
    sialangDescription: str
    sialangImage: str
    sialangBadge: str
    sialangStat: str
    sialangQuote: str
    peatTitle: str
    peatDescription: str
    peatQuote: str
    peatImages: list[str]
    recoveryTitle: str
    recoveryDescription: str
    recoveryItems: list[HomepageRecoveryItemOut]
    potentialTitle: str
    potentials: list[HomepagePotentialOut]
    potentialQuote: str
    potentialOpportunitiesTitle: str
    potentialOpportunityItems: list[HomepagePotentialOpportunityItemOut]
    facilitiesTitle: str
    facilities: list[HomepageFacilityOut]
    galleryTitle: str
    galleryDescription: str
    gallery: list[HomepageGalleryItemOut]
    contactTitle: str
    contactDescription: str
    footerLinks: list[HomepageFooterLinkOut]
    footerDescription: str
    officeHours: list[HomepageOfficeHourOut]
    footerBadges: list[str]
    footerCopyright: str


class HomepageAdminContentOut(HomepageDataOut):
    contactAddressSource: str = Field(..., alias="contactAddressSource")
    villageNameSource: str = Field(..., alias="villageNameSource")
