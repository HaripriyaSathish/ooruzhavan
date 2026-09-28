"""
Seed landing page content.

    python manage.py seed_data                  # seed every section
    python manage.py seed_data --section hero   # seed one section

Safe to run again: text is updated in place, and uploaded images are never touched.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from landing.models import (
    BusinessTypeOption,
    CustomerSection,
    CustomerType,
    EnquiryFormField,
    EnquiryPanelPoint,
    EnquirySection,
    FeaturedProduct,
    FeaturedProductSection,
    FooterBottomItem,
    FooterSection,
    HeroFeature,
    HeroSection,
    NavMenuItem,
    ProcessSection,
    ProcessStep,
    ProductCategory,
    ProductSection,
    SiteSettings,
    SocialLink,
    TopBarHighlight,
    WhyUsPoint,
    WhyUsSection,
)

DEFAULT_WHATSAPP_MESSAGE = 'வணக்கம் ஊர் உழவன்! எனது தேவைப் பட்டியலை அனுப்ப விரும்புகிறேன்.'


OLD_PLACEHOLDERS = {'', '+919999999999', '919999999999', 'info@ooruzhavan.com'}


def keep_or_set(current, value):
    return value if (current or '') in OLD_PLACEHOLDERS else current


def sync_list(model, key_field, rows, **extra):
    """Create/update rows matched on key_field. Order follows list position."""
    for index, row in enumerate(rows, start=1):
        lookup = {key_field: row[key_field], **extra}
        defaults = {**row, 'order': index}
        defaults.pop(key_field)
        model.objects.update_or_create(**lookup, defaults=defaults)


# ------------------------------------------------------------
# SECTION 1: TOP BAR + HEADER
# ------------------------------------------------------------
def seed_header():
    settings = SiteSettings.load()
    settings.site_name = 'ஊர் உழவன்'
    settings.tagline = 'மொத்த விற்பனை'
    settings.location = 'தமிழ்நாடு'
    settings.topbar_phone_label = 'தொடர்புக்கு'
    settings.topbar_email_label = 'மின்னஞ்சல்'
    settings.header_cta_text = 'தேவைப் பட்டியலை அனுப்புங்கள்'
    settings.header_cta_icon = 'fa-regular fa-paper-plane'
    settings.show_floating_whatsapp = True
    settings.show_floating_call = True
    # Real contact details. Only replaced when empty or still the old placeholder,
    # so anything changed later in admin is never overwritten.
    settings.phone_number = keep_or_set(settings.phone_number, '+91 99940 21305')
    settings.email = keep_or_set(settings.email, 'orders@oorulava.com')
    settings.whatsapp_number = keep_or_set(settings.whatsapp_number, '919994021305')
    settings.whatsapp_default_message = settings.whatsapp_default_message or DEFAULT_WHATSAPP_MESSAGE
    settings.save()

    sync_list(TopBarHighlight, 'text', [
        {'text': 'புதிய பொருட்கள்'},
        {'text': 'சொந்த விலை'},
        {'text': 'குறித்த நேர டெலிவரி'},
    ])

    sync_list(NavMenuItem, 'target_section', [
        {'target_section': 'home', 'label': 'முகப்பு'},
        {'target_section': 'products', 'label': 'பொருட்கள்'},
        {'target_section': 'process', 'label': 'செயல்முறை'},
        {'target_section': 'bulk-order', 'label': 'மொத்த ஆர்டர்'},
        {'target_section': 'about', 'label': 'எங்களைப் பற்றி'},
        {'target_section': 'contact', 'label': 'தொடர்புக்கு'},
    ])


# ------------------------------------------------------------
# SECTION 1: HERO
# ------------------------------------------------------------
def seed_hero():
    hero = HeroSection.load()
    hero.title = (
        '“உங்கள் வணிகத்திற்குத் தேவையான புதிய காய்கறிகள் மற்றும் பழங்கள் — '
        'நம்பிக்கையுடன் நேரடியாக விநியோகம்.”'
    )
    hero.description = (
        '“திருமண நிகழ்ச்சி,ஹோட்டல்கள், கேட்டரிங், காய்கறி மற்றும் பழக்கடைகளுக்கான '
        'தேவையான மொத்த காய்கறிகள், பழங்கள், அரிசி, மளிகைப் பொருட்கள் மற்றும் பிற '
        'அத்தியாவசியப் பொருட்கள் — அனைத்தும் நேரடியாக உங்கள் இடத்திற்கு.'
    )
    hero.primary_button_text = 'தேவைப் பட்டியலை அனுப்புங்கள்'
    hero.primary_button_icon = 'fa-regular fa-paper-plane'
    hero.secondary_button_text = 'பொருட்களைப் பாருங்கள்'
    hero.secondary_button_target = 'products'
    hero.is_active = True
    hero.save()

    sync_list(HeroFeature, 'text', [
        {'text': 'புதிய பொருட்கள்', 'icon': 'fa-solid fa-leaf'},
        {'text': 'மொத்த விலை', 'icon': 'fa-solid fa-coins'},
        {'text': 'இடத்திற்கு டெலிவரி', 'icon': 'fa-solid fa-truck-fast'},
    ], hero=hero)



# ------------------------------------------------------------
# SECTION 2: PRODUCT CATEGORIES
# ------------------------------------------------------------
def seed_products():
    section = ProductSection.load()
    section.badge_icon = 'fa-solid fa-sitemap'
    section.badge_text = 'முழுமையான வணிக தீர்வு'
    section.title = 'பொருட்களின் வகைகள்'
    section.description = (
        'உங்கள் வணிகம் மற்றும் விசேஷங்களுக்கு தேவையான {count} முக்கிய பிரிவுகளில் '
        'தரமான புதிய பொருட்கள் மொத்த அளவில் கிடைக்கும்.'
    )
    section.default_button_text = 'மொத்த விலை கேட்க'
    section.is_active = True
    section.save()

    sync_list(ProductCategory, 'tag', [
        {
            'tag': 'Fresh Vegetables',
            'name': 'புதிய காய்கறிகள்',
            'description': 'தக்காளி, வெங்காயம், உருளைக்கிழங்கு, கேரட், பீன்ஸ், முட்டைக்கோஸ் '
                           'உள்ளிட்ட அனைத்து பருவகால காய்கறிகள்.',
            'button_text': '',
            'whatsapp_message': 'வணக்கம்! புதிய காய்கறிகள் மொத்த விலை விவரம் தேவை.',
        },
        {
            'tag': 'Fresh Fruits',
            'name': 'புதிய பழங்கள்',
            'description': 'வாழைப்பழ தார்கள், ஆப்பிள், ஆரஞ்சு, எலுமிச்சை, மாதுளை, தர்பூசணி '
                           'மற்றும் ஜூஸ் பழ வகைகள்.',
            'button_text': '',
            'whatsapp_message': 'வணக்கம்! புதிய பழங்கள் மொத்த விலை விவரம் தேவை.',
        },
        {
            'tag': 'Rice & Grains',
            'name': 'அரிசி மற்றும் தானியங்கள்',
            'description': 'பொன்னி, இட்லி அரிசி, சீரக சம்பா, பாஸ்மதி, கம்பு, சோளம் மற்றும் '
                           'உயர்தர தானிய வகைகள் (25/50kg மூட்டைகள்).',
            'button_text': '',
            'whatsapp_message': 'வணக்கம்! அரிசி மற்றும் தானியங்கள் மொத்த விலை விவரம் தேவை.',
        },
        {
            'tag': 'Grocery & Pulses',
            'name': 'மளிகைப் பொருட்கள் & பருப்பு வகைகள்',
            'description': 'துவரம் பருப்பு, உளுந்து, பாசிப்பருப்பு, கடலைப்பருப்பு, சர்க்கரை '
                           'மற்றும் முழு மளிகை சரக்குகள்.',
            'button_text': '',
            'whatsapp_message': 'வணக்கம்! மளிகைப் பொருட்கள் & பருப்பு வகைகள் மொத்த விலை விவரம் தேவை.',
        },
        {
            'tag': 'Oil & Spices',
            'name': 'எண்ணெய் மற்றும் மசாலாப் பொருட்கள்',
            'description': 'கடலை எண்ணெய், நல்லெண்ணெய், சூரியகாந்தி எண்ணெய் டின் & கேன்கள், '
                           'மிளகு, சீரகம், ஏலக்காய், பட்டை கிராம்பு.',
            'button_text': '',
            'whatsapp_message': 'வணக்கம்! எண்ணெய் மற்றும் மசாலாப் பொருட்கள் மொத்த விலை விவரம் தேவை.',
        },
        {
            'tag': 'Catering Supplies',
            'name': 'கேட்டரிங் & விசேஷ பொருட்கள்',
            'description': 'வாழை இலை கட்டுகள், பொள்ளாச்சி தேங்காய், தாம்பூலம் பொருட்கள், '
                           'பூக்கள் மற்றும் பிரத்யேக திருமண சமையல் தொகுப்பு.',
            'button_text': '',
            'whatsapp_message': 'வணக்கம்! கேட்டரிங் & விசேஷ பொருட்கள் மொத்த விலை விவரம் தேவை.',
        },
        {
            'tag': 'Hotel & Restaurant Supplies',
            'name': 'ஹோட்டல் & உணவக தேவைகள்',
            'description': 'தினசரி கட் காய்கறி சப்ளை, இஞ்சி, பூண்டு மொத்த சரக்குகள், வெங்காயம், '
                           'தக்காளி கிரேட்கள், சமையல் கூடம் மற்றும் உணவகங்களுக்கான '
                           'மாதாந்திர/வாராந்திர ஒப்பந்த சப்ளை.',
            'button_text': 'வணிக ஒப்பந்தம் பேசுக',
            'whatsapp_message': 'வணக்கம்! எங்கள் ஹோட்டல் / உணவகத்திற்கான வணிக ஒப்பந்த சப்ளை பற்றி பேச விரும்புகிறேன்.',
        },
    ])



# ------------------------------------------------------------
# SECTION 3: WHO WE SERVE / B2B CUSTOMERS
# ------------------------------------------------------------
def seed_customers():
    section = CustomerSection.load()
    section.badge_icon = 'fa-solid fa-users'
    section.badge_text = 'B2B வணிக கூட்டாளர்கள்'
    section.title = 'யாருக்கு விநியோகிக்கிறோம்?'
    section.description = (
        'மொத்த கொள்முதல் செய்யும் வணிக நிறுவனங்கள் மற்றும் விழாக்களுக்கு ஏற்றவாறு '
        'பிரத்யேக B2B சேவை மற்றும் விலை.'
    )
    section.is_active = True
    section.save()

    sync_list(CustomerType, 'name', [
        {
            'name': 'ஹோட்டல்கள் (Hotels)',
            'icon': 'fa-solid fa-hotel',
            'subtitle': 'நட்சத்திர & தங்கும் விடுதிகள்',
            'description': 'உயர் தரம் பிரிக்கப்பட்ட காய்கறிகள், பிரீமியம் அரிசி, மளிகைப் '
                           'பொருட்கள் தினசரி காலை விநியோகம்.',
            'key_point': 'தொடர்ச்சியான தினசரி சப்ளை',
            'highlight': 'B2B ரேட்ஸ்',
        },
        {
            'name': 'உணவகங்கள் (Restaurants)',
            'icon': 'fa-solid fa-utensils',
            'subtitle': 'மெஸ், தாபா & ஃபாஸ்ட் புட்ஸ்',
            'description': 'அன்றாட சமையலுக்குத் தேவையான பெரிய வெங்காயம், நாட்டு தக்காளி, '
                           'உருளை, மசாலா பொருட்கள் மற்றும் எண்ணெய் வகைகள்.',
            'key_point': 'கிரேட்கள் மற்றும் மூட்டை விலை',
            'highlight': 'குறைந்த சேதாரம்',
        },
        {
            'name': 'கேட்டரிங் சர்வீசஸ் (Catering Services)',
            'icon': 'fa-solid fa-kitchen-set',
            'subtitle': 'நிகழ்வு சமையல் ஒப்பந்தக்காரர்கள்',
            'description': 'ஒரே பட்டியலில் அத்தனை பொருட்களையும் குறித்த நேரத்தில் சமையல் '
                           'கூடம் உள்ள இடத்திற்கே கொண்டு சேர்த்தல்.',
            'key_point': 'முழுமையான பட்டியல் பேக்கிங்',
            'highlight': '24/7 சேவை',
        },
        {
            'name': 'திருமண நிகழ்ச்சிகள் & விழாக்கள்',
            'icon': 'fa-solid fa-bell-concierge',
            'subtitle': 'மண்டபங்கள் & சமூக விருந்துகள்',
            'description': 'வாழைப்பழ தார், தேங்காய், பந்தி இலைகள், சீரக சம்பா, நெய், '
                           'எண்ணெய் மற்றும் காய்கறி மொத்த தொகுப்புகள்.',
            'key_point': 'மண்டபத்திற்கே நேரடி வேன்',
            'highlight': 'மொத்த சேமிப்பு',
        },
        {
            'name': 'காய்கறி & பழக்கடைகள் (Retail Shops)',
            'icon': 'fa-solid fa-store',
            'subtitle': 'சில்லறை விற்பனையாளர்கள்',
            'description': 'சில்லறை விற்பனையாளர்களுக்கு அன்றைய சந்தை விலைக்கேற்ப மொத்த '
                           'கிரேட்கள், பெட்டிகள் மற்றும் சாக்கு மூட்டைகளில் நேரடி விநியோகம்.',
            'key_point': 'மண்டியில் இருந்து நேரடி மூட்டை',
            'highlight': 'மண்டி விலை',
        },
        {
            'name': 'பிற வணிக நிறுவனங்கள் (B2B)',
            'icon': 'fa-solid fa-building',
            'subtitle': 'ஹாஸ்டல்கள், கேன்டீன்கள் & நிறுவனங்கள்',
            'description': 'கல்லூரி, தொழிற்சாலை விடுதிகள், தனியார் நிறுவன கேன்டீன்களுக்கான '
                           'வழக்கமான வாராந்திர/மாதாந்திர கொள்முதல் தேவைகள்.',
            'key_point': 'ஜிஎஸ்டி பில் & முறைப்படுத்தப்பட்ட சப்ளை',
            'highlight': 'B2B பில்லிங்',
        },
    ])



# ------------------------------------------------------------
# SECTION 4: HOW IT WORKS / PROCESS
# ------------------------------------------------------------
def seed_process():
    section = ProcessSection.load()
    section.title = 'எப்படி செயல்படுகிறது?'
    section.description = 'உங்கள் நிகழ்வு இடத்திற்கு மிக எளிதாக — சிரமமில்லாமல்.'
    section.step_prefix = 'படி'
    section.is_active = True
    section.save()

    sync_list(ProcessStep, 'title', [
        {
            'title': 'பட்டியல் அனுப்பவும்',
            'icon': 'fa-solid fa-clipboard-list',
            'description': 'உங்களுக்குத் தேவையான பொருட்கள் மற்றும் அவற்றின் அளவை அனுப்பவும்.',
            'tag': 'Form / WhatsApp / Excel',
        },
        {
            'title': 'விலை & இருப்பு உறுதி',
            'icon': 'fa-solid fa-file-invoice-dollar',
            'description': 'பொருட்களின் இருப்பு மற்றும் மொத்த விலையை நாங்கள் உறுதி செய்வோம்.',
            'tag': 'உடனடி Quoting & Stock Check',
        },
        {
            'title': 'ஆர்டர் கன்ஃபர்மேஷன்',
            'icon': 'fa-solid fa-circle-check',
            'description': 'ஆர்டரை உறுதிசெய்யவும்.',
            'tag': 'பொருட்கள் தரம் பிரிப்பு & பேக்கிங்',
        },
        {
            'title': 'நேரடி டெலிவரி',
            'icon': 'fa-solid fa-truck-ramp-box',
            'description': 'உறுதிசெய்யப்பட்ட ஆர்டரை நேரடியாக உங்கள் இடத்திற்கு வழங்குவோம்.',
            'tag': 'குறித்த நேரத்தில் உங்கள் இடத்தில்',
        },
    ])



# ------------------------------------------------------------
# SECTION 5: FEATURED PRODUCTS
# ------------------------------------------------------------
def seed_featured():
    section = FeaturedProductSection.load()
    section.badge_icon = ''
    section.badge_text = 'புதிய வருகை & மொத்த ஸ்டாக்'
    section.title = 'முக்கிய பொருட்கள்'
    section.description = (
        'நம்பகமான விவசாயிகளிடமிருந்தும் மொத்த சந்தைகளிலும் இருந்து பெறப்படும் '
        'தரமான புதிய பொருட்கள்.'
    )
    section.button_text = 'விலை கேட்க'
    section.button_icon = 'fa-brands fa-whatsapp'
    section.is_active = True
    section.save()

    sync_list(FeaturedProduct, 'name', [
        {'name': 'வாழைப்பழம்', 'tag': 'பழங்கள்',
         'description': 'பூவன், செவ்வாழை, ரோபஸ்டா மொத்த தார்'},
        {'name': 'தக்காளி', 'tag': 'காய்கறிகள்',
         'description': 'நாட்டு தக்காளி & ஆப்பிள் தக்காளி கிரேட்கள்'},
        {'name': 'வெங்காயம்', 'tag': 'காய்கறிகள்',
         'description': 'சின்ன வெங்காயம், பல்லாரி மூட்டைகள்'},
        {'name': 'உருளைக்கிழங்கு', 'tag': 'காய்கறிகள்',
         'description': 'ஊட்டி மற்றும் மேட்டுப்பாளையம் தரம்'},
        {'name': 'கேரட் (ஊட்டி)', 'tag': 'காய்கறிகள்',
         'description': 'புதிய மலைத்தோட்ட கேரட் மூட்டைகள்'},
        {'name': 'அரிசி வகைகள்', 'tag': 'மளிகை',
         'description': 'பொன்னி, சீரக சம்பா, பாஸ்மதி அரிசி'},
        {'name': 'பருப்பு வகைகள்', 'tag': 'மளிகை',
         'description': 'துவரம் பருப்பு, உளுந்து, பாசிப்பருப்பு'},
        {'name': 'தேங்காய்', 'tag': 'விழா சிறப்பு',
         'description': 'பொள்ளாச்சி சமையல் & தாம்பூல தேங்காய்'},
    ])


# ------------------------------------------------------------
# SECTION 6: BULK ORDER / WHOLESALE ENQUIRY
# ------------------------------------------------------------
def seed_enquiry():
    section = EnquirySection.load()
    # Left panel
    section.panel_badge_text = 'ஊர் உழவன் B2B விநியோகம்'
    section.panel_title = 'உங்கள் வணிகத்திற்குத் தேவையான அனைத்து பொருட்களும்'
    section.panel_title_highlight = 'ஒரே இடத்தில்!'
    section.panel_description = (
        'தினசரி மண்டி விலையிலேயே சிறந்த தரமான காய்கறிகள், பழங்கள் மற்றும் மளிகைப் '
        'பொருட்கள் நேரடியாக உங்கள் வணிக இடத்திற்கு வந்து சேரும்.'
    )
    # Form header
    section.form_title = 'மொத்த விலை விசாரணை படிவம் (Wholesale Enquiry)'
    section.form_description = (
        'கீழே உள்ள படிவத்தை பூர்த்தி செய்து உடனடி விலைப் பட்டியல் மற்றும் '
        'விநியோக விவரங்களைப் பெறுங்கள்.'
    )
    section.form_badge_icon = 'fa-solid fa-bolt'
    section.form_badge_text = 'உடனடி பதில்'
    # Upload box
    section.upload_icon = 'fa-solid fa-arrow-up-from-bracket'
    section.upload_title = 'தேவைப் பட்டியல் கோப்பை பதிவேற்றலாம்'
    section.upload_hint = '(Excel, PDF, Handwritten Sheet அல்லது Image)'
    section.max_files = 5
    section.max_file_size_mb = 10
    # WhatsApp box
    section.whatsapp_box_title = 'வாட்ஸ்அப் நேரடி ஆர்டர்'
    section.whatsapp_box_text = (
        'உங்கள் மளிகை/காய்கறி பட்டியலை போட்டோ அல்லது மெசேஜாக நேரடியாக அனுப்பலாம்.'
    )
    section.whatsapp_button_text = 'வாட்ஸ்அப்பில் பட்டியலை அனுப்ப'
    section.whatsapp_message = 'வணக்கம் ஊர் உழவன்! எனது தேவைப் பட்டியலை இங்கே அனுப்புகிறேன்.'
    # Submit
    section.submit_button_icon = 'fa-regular fa-paper-plane'
    section.submit_button_text = 'மொத்த விலை கோரிக்கை சமர்ப்பிக்க (Submit Wholesale Enquiry)'
    section.success_message = (
        'நன்றி! உங்கள் மொத்த விலை விசாரணை பெறப்பட்டது. '
        'எங்கள் குழு விரைவில் உங்களைத் தொடர்பு கொள்ளும்.'
    )
    section.open_whatsapp_after_submit = True
    section.is_active = True
    section.save()

    sync_list(EnquiryPanelPoint, 'text', [
        {'text': 'ஹோட்டல் & கேட்டரிங் சிறப்புத் தேவைகள்'},
        {'text': 'வணிக வாடிக்கையாளர் மொத்த விலை'},
        {'text': 'குறித்த நேர டெலிவரி உத்தரவாதம்'},
    ], section=section)

    sync_list(EnquiryFormField, 'key', [
        {
            'key': 'business_name',
            'label': 'வணிகம் / வாடிக்கையாளர் பெயர் (Business/Customer Name)',
            'placeholder': 'எ.கா. அன்னபூர்ணா கேட்டரிங் / ஹோட்டல்',
            'icon': 'fa-regular fa-building',
            'is_required': True,
        },
        {
            'key': 'contact_person',
            'label': 'தொடர்பு கொள்ள வேண்டிய நபர் (Contact Person)',
            'placeholder': 'உங்கள் பெயர்',
            'icon': 'fa-regular fa-user',
            'is_required': True,
        },
        {
            'key': 'mobile',
            'label': 'கைபேசி எண் / WhatsApp (Mobile Number)',
            'placeholder': '10 இலக்க மொபைல் எண்',
            'icon': 'fa-solid fa-phone',
            'is_required': True,
        },
        {
            'key': 'business_type',
            'label': 'வணிக வகை (Business Type)',
            'placeholder': 'வணிக வகையைத் தேர்ந்தெடுக்கவும்',
            'icon': 'fa-solid fa-briefcase',
            'is_required': True,
        },
        {
            'key': 'delivery_location',
            'label': 'விநியோக இடம் / முகவரி (Delivery Location)',
            'placeholder': 'மண்டபம்/கடை/ஹோட்டல் முகவரி மற்றும் ஊர்',
            'icon': 'fa-solid fa-location-dot',
            'is_required': True,
        },
        {
            'key': 'delivery_date',
            'label': 'தேவையான விநியோக தேதி (Delivery Date)',
            'placeholder': '',
            'icon': 'fa-regular fa-calendar',
            'is_required': True,
        },
        {
            'key': 'required_products',
            'label': 'தேவையான பொருட்கள் (Required Products)',
            'placeholder': 'எ.கா. தக்காளி, வெங்காயம், உருளை, அரிசி...',
            'icon': 'fa-solid fa-basket-shopping',
            'is_required': True,
        },
        {
            'key': 'quantity',
            'label': 'தோராயமான அளவு / எடையளவு (Approx Quantity)',
            'placeholder': 'எ.கா. 50 kg, 200 kg, 10 மூட்டை',
            'icon': 'fa-solid fa-scale-balanced',
            'is_required': True,
        },
        {
            'key': 'message',
            'label': 'கூடுதல் தகவல் / குறிப்புகள் (Additional Message)',
            'placeholder': 'குறிப்பிட்ட தரம், கட் காய்கறி தேவை அல்லது சிறப்பு விவரங்களை இங்கே குறிப்பிடவும்...',
            'icon': '',
            'is_required': False,
        },
    ])

    sync_list(BusinessTypeOption, 'name', [
        {'name': 'ஹோட்டல் (Hotel)'},
        {'name': 'உணவகம் (Restaurant)'},
        {'name': 'கேட்டரிங் சர்வீஸ் (Catering Service)'},
        {'name': 'திருமண மண்டபம் / விழா (Wedding / Event)'},
        {'name': 'காய்கறி & பழக்கடை (Retail Shop)'},
        {'name': 'ஹாஸ்டல் / கேன்டீன் (Hostel / Canteen)'},
        {'name': 'மற்றவை (Other)'},
    ])


# ------------------------------------------------------------
# SECTION 7: WHY CHOOSE US
# ------------------------------------------------------------
def seed_why_us():
    section = WhyUsSection.load()
    section.badge_icon = 'fa-solid fa-award'
    section.badge_text = 'எங்கள் சிறப்பம்சங்கள்'
    section.title = 'ஏன் ஊர் உழவன்?'
    section.description = (
        'தமிழ்நாட்டில் ஹோட்டல்கள், உணவகங்கள், கேட்டரிங் மற்றும் திருமண வணிக '
        'வாடிக்கையாளர்களுக்கு நம்பகமான நேரடி சப்ளை பார்ட்னர்.'
    )
    section.is_active = True
    section.save()

    sync_list(WhyUsPoint, 'title', [
        {
            'title': 'ஒரே இடத்தில் அனைத்தும்',
            'icon': 'fa-solid fa-basket-shopping',
            'description': 'காய்கறிகள், பழங்கள் மற்றும் முழுமையான மளிகைப் பொருட்கள் '
                           'அனைத்தும் ஒரே சப்ளையரிடம்.',
        },
        {
            'title': 'B2B மொத்த விலை',
            'icon': 'fa-solid fa-hand-holding-dollar',
            'description': 'வணிக வாடிக்கையாளர்களுக்கான அதிக சேமிப்பு தரும் நேரடி '
                           'மார்க்கெட் மொத்த விற்பனை விலை.',
        },
        {
            'title': 'ஹோட்டல் & கேட்டரிங் சிறப்புத் தேவைகள்',
            'icon': 'fa-solid fa-kitchen-set',
            'description': 'அளவு, தரம் மற்றும் குறிப்பிட்ட சமையல் முறைகளுக்கு உகந்த '
                           'பிரத்யேக தயாரிப்பு மற்றும் கிரேடுகள்.',
        },
        {
            'title': 'ஆர்டர் நேரடி விநியோகம்',
            'icon': 'fa-solid fa-truck-fast',
            'description': 'உங்கள் தேவைக்கேற்ப தொகுக்கப்பட்டு குறித்த நேரத்தில் விழா '
                           'அல்லது வணிக இடத்திற்கே விநியோகம்.',
        },
        {
            'title': 'நம்பகமான ஆதரவு',
            'icon': 'fa-solid fa-headset',
            'description': 'அவசரத் தேவைகள் மற்றும் தினசரி ஆர்டர்களுக்கு உடனடி WhatsApp '
                           'மற்றும் தொலைபேசி வாடிக்கையாளர் உதவி.',
        },
    ])


# ------------------------------------------------------------
# SECTION 8: FOOTER
# ------------------------------------------------------------
def seed_footer():
    footer = FooterSection.load()
    footer.description = (
        'திருமணம், நிகழ்வுகள் மற்றும் பெரிய அளவிலான சமையல் தேவைகளுக்கான பழங்கள், '
        'காய்கறிகள், மளிகைப் பொருட்கள் மொத்த விலையில் தமிழ்நாட்டில்.'
    )
    footer.quick_links_title = 'விரைவு இணைப்புகள்'
    footer.contact_title = 'தொடர்புக்கு'
    footer.address = 'மொத்த வியாபார வளாகம்,\nதமிழ்நாடு - 641001'
    footer.service_note = '24/7 திருமண ஆர்டர் சேவை'
    footer.social_title = 'எங்களைப் பின்தொடருங்கள்'
    footer.whatsapp_button_text = 'வாட்ஸ்அப்பில் நேரடிகள்'
    footer.whatsapp_message = ''
    footer.copyright_text = '© {year} ஊர் உழவன்  மொத்த விற்பனை. அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.'
    footer.save()

    # Links are placeholders; replace with real profile URLs in admin
    for index, row in enumerate([
        {'name': 'Facebook', 'icon': 'fa-brands fa-facebook-f', 'url': 'https://www.facebook.com/'},
        {'name': 'Instagram', 'icon': 'fa-brands fa-instagram', 'url': 'https://www.instagram.com/'},
        {'name': 'YouTube', 'icon': 'fa-brands fa-youtube', 'url': 'https://www.youtube.com/'},
    ], start=1):
        link, created = SocialLink.objects.get_or_create(name=row['name'], defaults={**row, 'order': index})
        if not created:  # keep a real URL added in admin
            link.icon, link.order = row['icon'], index
            link.save()

    sync_list(FooterBottomItem, 'text', [
        {'text': 'புதிய பொருட்கள்'},
        {'text': 'மொத்த விலை'},
        {'text': 'இடத்திற்கு டெலிவரி'},
        {'text': 'தமிழ்நாடு'},
    ])


SECTIONS = {
    'header': seed_header,
    'hero': seed_hero,
    'products': seed_products,
    'customers': seed_customers,
    'process': seed_process,
    'featured': seed_featured,
    'enquiry': seed_enquiry,
    'why-us': seed_why_us,
    'footer': seed_footer,
}


class Command(BaseCommand):
    help = 'Seed landing page content (Tamil) for all or one section.'

    def add_arguments(self, parser):
        parser.add_argument('--section', choices=SECTIONS.keys(), help='Seed only this section')

    @transaction.atomic
    def handle(self, *args, **options):
        names = [options['section']] if options['section'] else list(SECTIONS)
        for name in names:
            SECTIONS[name]()
            self.stdout.write(self.style.SUCCESS(f'✔ Seeded: {name}'))
