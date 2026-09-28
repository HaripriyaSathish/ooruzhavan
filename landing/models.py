from urllib.parse import quote

from django.db import models


# ------------------------------------------------------------
# BASE CLASSES
# ------------------------------------------------------------
class SingletonModel(models.Model):
    """A model that only ever has one row (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Singletons cannot be deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OrderedItem(models.Model):
    """Common fields for list items shown in admin-defined order."""

    order = models.PositiveIntegerField('Display order', default=0)
    is_active = models.BooleanField('Show on website', default=True)

    class Meta:
        abstract = True
        ordering = ['order', 'id']


ICON_HELP = 'Font Awesome class, e.g. "fa-solid fa-leaf". Browse icons at fontawesome.com/icons'


# ------------------------------------------------------------
# SECTION 1: SITE SETTINGS (top bar, header, WhatsApp, floating buttons)
# ------------------------------------------------------------
class SiteSettings(SingletonModel):
    # Branding
    site_name = models.CharField('Site name', max_length=100)
    tagline = models.CharField('Tagline (under logo)', max_length=100, blank=True)
    logo = models.ImageField('Logo', upload_to='ooruzhavan/branding/', blank=True, null=True)

    # Contact details
    phone_number = models.CharField(
        'Phone number', max_length=20,
        help_text='With country code, e.g. +919876543210',
    )
    email = models.EmailField('Email address')
    location = models.CharField('Location', max_length=100)

    # Top bar labels
    topbar_phone_label = models.CharField('Top bar: phone label', max_length=50)
    topbar_email_label = models.CharField('Top bar: email label', max_length=50)

    # WhatsApp
    whatsapp_number = models.CharField(
        'WhatsApp number', max_length=20,
        help_text='Digits only with country code, no + or spaces, e.g. 919876543210',
    )
    whatsapp_default_message = models.TextField(
        'Default WhatsApp message',
        help_text='Pre-filled message when a visitor taps any WhatsApp button',
    )

    # Header button
    header_cta_text = models.CharField('Header button text', max_length=100)
    header_cta_icon = models.CharField('Header button icon', max_length=60, blank=True, help_text=ICON_HELP)

    # Floating buttons
    show_floating_whatsapp = models.BooleanField('Show floating WhatsApp button', default=True)
    show_floating_call = models.BooleanField('Show floating call button', default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return self.site_name or 'Site settings'

    def whatsapp_link(self, message=None):
        text = quote(message or self.whatsapp_default_message)
        return f'https://wa.me/{self.whatsapp_number}?text={text}'

    @property
    def phone_link(self):
        return f"tel:{self.phone_number.replace(' ', '')}"


class TopBarHighlight(OrderedItem):
    """Right side of the top bar: புதிய பொருட்கள் | சொந்த விலை | ..."""

    text = models.CharField('Text', max_length=100)

    class Meta(OrderedItem.Meta):
        verbose_name = 'Top bar highlight'
        verbose_name_plural = 'Top bar highlights'

    def __str__(self):
        return self.text


class NavMenuItem(OrderedItem):
    label = models.CharField('Menu label', max_length=100)
    target_section = models.CharField(
        'Target section id', max_length=50,
        help_text='Section id on the page without #, e.g. "products"',
    )

    class Meta(OrderedItem.Meta):
        verbose_name = 'Navigation menu item'
        verbose_name_plural = 'Navigation menu items'

    def __str__(self):
        return self.label


# ------------------------------------------------------------
# SECTION 1: HERO
# ------------------------------------------------------------
class HeroSection(SingletonModel):
    title = models.TextField('Heading')
    description = models.TextField('Description')
    background_image = models.ImageField(
        'Background image', upload_to='ooruzhavan/hero/', blank=True, null=True,
        help_text='Recommended: 1920 x 1000 px, landscape',
    )

    # Primary button -> WhatsApp
    primary_button_text = models.CharField('Primary button text', max_length=100)
    primary_button_icon = models.CharField('Primary button icon', max_length=60, blank=True, help_text=ICON_HELP)
    primary_button_whatsapp_message = models.TextField(
        'Primary button WhatsApp message', blank=True,
        help_text='Leave empty to use the default WhatsApp message from Site settings',
    )

    # Secondary button -> scroll to section
    secondary_button_text = models.CharField('Secondary button text', max_length=100)
    secondary_button_target = models.CharField(
        'Secondary button target section id', max_length=50,
        help_text='Section id without #, e.g. "products"',
    )

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero section'
        verbose_name_plural = 'Hero section'

    def __str__(self):
        return 'Hero section'


class HeroFeature(OrderedItem):
    """Small icon + text row under the hero buttons."""

    hero = models.ForeignKey(HeroSection, on_delete=models.CASCADE, related_name='features')
    icon = models.CharField('Icon', max_length=60, help_text=ICON_HELP)
    text = models.CharField('Text', max_length=100)

    class Meta(OrderedItem.Meta):
        verbose_name = 'Hero feature'
        verbose_name_plural = 'Hero features'

    def __str__(self):
        return self.text


# ------------------------------------------------------------
# SECTION 2: PRODUCT CATEGORIES (id="products")
# ------------------------------------------------------------
class ProductSection(SingletonModel):
    badge_icon = models.CharField('Badge icon', max_length=60, blank=True, help_text=ICON_HELP)
    badge_text = models.CharField('Badge text', max_length=100, blank=True)
    title = models.CharField('Heading', max_length=200)
    description = models.TextField(
        'Description',
        help_text='Write {count} where the number of categories should appear. '
                  'It is replaced automatically with the number of active categories.',
    )
    default_button_text = models.CharField(
        'Default card button text', max_length=100,
        help_text='Used on every category card unless the category has its own button text',
    )

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Products section'
        verbose_name_plural = 'Products section'

    def __str__(self):
        return 'Products section'

    @property
    def description_display(self):
        count = ProductCategory.objects.filter(is_active=True).count()
        return self.description.replace('{count}', str(count))


class ProductCategory(OrderedItem):
    tag = models.CharField(
        'Image tag (English)', max_length=60,
        help_text='Small label on the image corner, e.g. "Fresh Vegetables"',
    )
    name = models.CharField('Category name', max_length=150)
    description = models.TextField('Description')
    image = models.ImageField(
        'Image', upload_to='ooruzhavan/products/', blank=True, null=True,
        help_text='Recommended: 800 x 460 px, landscape',
    )
    button_text = models.CharField(
        'Button text', max_length=100, blank=True,
        help_text='Leave empty to use the default card button text from Products section',
    )
    whatsapp_message = models.TextField(
        'WhatsApp message', blank=True,
        help_text='Leave empty to auto-generate: "வணக்கம்! <category name> மொத்த விலை விவரம் தேவை."',
    )

    class Meta(OrderedItem.Meta):
        verbose_name = 'Product category'
        verbose_name_plural = 'Product categories'

    def __str__(self):
        return f'{self.name} ({self.tag})'

    @property
    def whatsapp_message_text(self):
        return self.whatsapp_message or f'வணக்கம்! {self.name} மொத்த விலை விவரம் தேவை.'


# ------------------------------------------------------------
# SECTION 3: WHO WE SERVE / B2B CUSTOMERS (id="customers")
# ------------------------------------------------------------
class CustomerSection(SingletonModel):
    badge_icon = models.CharField('Badge icon', max_length=60, blank=True, help_text=ICON_HELP)
    badge_text = models.CharField('Badge text', max_length=100, blank=True)
    title = models.CharField('Heading', max_length=200)
    description = models.TextField('Description', blank=True)

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customers section (Who we serve)'
        verbose_name_plural = 'Customers section (Who we serve)'

    def __str__(self):
        return 'Customers section'


class CustomerType(OrderedItem):
    """One card: Hotels, Restaurants, Catering, etc."""

    icon = models.CharField('Icon', max_length=60, help_text=ICON_HELP)
    name = models.CharField('Customer type', max_length=150, help_text='e.g. "ஹோட்டல்கள் (Hotels)"')
    subtitle = models.CharField('Subtitle', max_length=150, blank=True, help_text='Green line under the name')
    description = models.TextField('Description')
    key_point = models.CharField('Bottom-left point', max_length=150, blank=True, help_text='Shown with a bullet •')
    highlight = models.CharField('Bottom-right highlight', max_length=60, blank=True, help_text='Short bold tag, e.g. "B2B ரேட்ஸ்"')

    class Meta(OrderedItem.Meta):
        verbose_name = 'Customer type'
        verbose_name_plural = 'Customer types'

    def __str__(self):
        return self.name


# ------------------------------------------------------------
# SECTION 4: HOW IT WORKS / PROCESS (id="process")
# ------------------------------------------------------------
class ProcessSection(SingletonModel):
    title = models.CharField('Heading', max_length=200)
    description = models.TextField('Description', blank=True)
    step_prefix = models.CharField(
        'Step prefix', max_length=30, default='படி',
        help_text='Shown before each step number, e.g. "படி" → "படி 1: பட்டியல் அனுப்பவும்". '
                  'Step numbers are automatic, based on display order.',
    )

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Process section (How it works)'
        verbose_name_plural = 'Process section (How it works)'

    def __str__(self):
        return 'Process section'


class ProcessStep(OrderedItem):
    icon = models.CharField('Icon', max_length=60, help_text=ICON_HELP)
    title = models.CharField(
        'Step title', max_length=150,
        help_text='Without "படி 1:" — the prefix and number are added automatically',
    )
    description = models.TextField('Description')
    tag = models.CharField('Tag (green pill)', max_length=100, blank=True)

    class Meta(OrderedItem.Meta):
        verbose_name = 'Process step'
        verbose_name_plural = 'Process steps'

    def __str__(self):
        return self.title

    @property
    def step_number(self):
        """Position among active steps (1, 2, 3...). None if hidden."""
        if not self.is_active:
            return None
        ids = list(ProcessStep.objects.filter(is_active=True).values_list('id', flat=True))
        return ids.index(self.id) + 1 if self.id in ids else None


# ------------------------------------------------------------
# SECTION 5: FEATURED PRODUCTS (id="featured-products")
# ------------------------------------------------------------
class FeaturedProductSection(SingletonModel):
    badge_icon = models.CharField('Badge icon', max_length=60, blank=True, help_text=ICON_HELP)
    badge_text = models.CharField('Badge text', max_length=100, blank=True)
    title = models.CharField('Heading', max_length=200)
    description = models.TextField('Description', blank=True)
    button_text = models.CharField('Card button text', max_length=100)
    button_icon = models.CharField('Card button icon', max_length=60, blank=True, help_text=ICON_HELP)

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Featured products section'
        verbose_name_plural = 'Featured products section'

    def __str__(self):
        return 'Featured products section'


class FeaturedProduct(OrderedItem):
    name = models.CharField('Product name', max_length=150)
    tag = models.CharField('Image tag', max_length=60, blank=True, help_text='Small label on the image, e.g. "காய்கறிகள்"')
    description = models.CharField('Short description', max_length=255)
    image = models.ImageField(
        'Image', upload_to='ooruzhavan/featured/', blank=True, null=True,
        help_text='Recommended: 600 x 380 px, landscape',
    )
    whatsapp_message = models.TextField(
        'WhatsApp message', blank=True,
        help_text='Leave empty to auto-generate: "வணக்கம்! <product name> மொத்த விலை விவரம் தேவை."',
    )

    class Meta(OrderedItem.Meta):
        verbose_name = 'Featured product'
        verbose_name_plural = 'Featured products'

    def __str__(self):
        return self.name

    @property
    def whatsapp_message_text(self):
        return self.whatsapp_message or f'வணக்கம்! {self.name} மொத்த விலை விவரம் தேவை.'


# ------------------------------------------------------------
# SECTION 6: BULK ORDER / WHOLESALE ENQUIRY (id="bulk-order")
# ------------------------------------------------------------
class EnquirySection(SingletonModel):
    # Left image panel
    panel_image = models.ImageField(
        'Panel image', upload_to='ooruzhavan/enquiry/', blank=True, null=True,
        help_text='Recommended: 700 x 1000 px, portrait',
    )
    panel_badge_text = models.CharField('Panel badge text', max_length=100, blank=True)
    panel_title = models.CharField('Panel heading', max_length=200)
    panel_title_highlight = models.CharField(
        'Panel heading (highlighted part)', max_length=100, blank=True,
        help_text='Shown in light green after the heading, e.g. "ஒரே இடத்தில்!"',
    )
    panel_description = models.TextField('Panel description', blank=True)

    # Form header
    form_title = models.CharField('Form heading', max_length=200)
    form_description = models.TextField('Form description', blank=True)
    form_badge_icon = models.CharField('Form badge icon', max_length=60, blank=True, help_text=ICON_HELP)
    form_badge_text = models.CharField('Form badge text', max_length=60, blank=True)

    # File upload box
    upload_icon = models.CharField('Upload icon', max_length=60, blank=True, help_text=ICON_HELP)
    upload_title = models.CharField('Upload box title', max_length=150)
    upload_hint = models.CharField('Upload box hint', max_length=150, blank=True)
    max_files = models.PositiveSmallIntegerField('Max files per enquiry', default=5)
    max_file_size_mb = models.PositiveSmallIntegerField(
        'Max size per file (MB)', default=10,
        help_text='Cloudinary free plan allows up to 10 MB per file',
    )

    # WhatsApp box
    whatsapp_box_title = models.CharField('WhatsApp box title', max_length=150)
    whatsapp_box_text = models.TextField('WhatsApp box text', blank=True)
    whatsapp_button_text = models.CharField('WhatsApp button text', max_length=100)
    whatsapp_message = models.TextField(
        'WhatsApp button message', blank=True,
        help_text='Leave empty to use the default WhatsApp message from Site settings',
    )

    # Submit
    submit_button_icon = models.CharField('Submit button icon', max_length=60, blank=True, help_text=ICON_HELP)
    submit_button_text = models.CharField('Submit button text', max_length=150)
    success_message = models.TextField('Success message', help_text='Shown after the form is submitted')
    open_whatsapp_after_submit = models.BooleanField(
        'Open WhatsApp after submit', default=True,
        help_text='After saving, open WhatsApp with the enquiry details pre-filled',
    )

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Enquiry section (Bulk order)'
        verbose_name_plural = 'Enquiry section (Bulk order)'

    def __str__(self):
        return 'Enquiry section'


class EnquiryPanelPoint(OrderedItem):
    """Green tick points at the bottom of the left panel."""

    section = models.ForeignKey(EnquirySection, on_delete=models.CASCADE, related_name='points')
    text = models.CharField('Text', max_length=150)

    class Meta(OrderedItem.Meta):
        verbose_name = 'Panel point'
        verbose_name_plural = 'Panel points'

    def __str__(self):
        return self.text


class EnquiryFormField(OrderedItem):
    """Label / placeholder / icon / required setting for each form input."""

    class Key(models.TextChoices):
        BUSINESS_NAME = 'business_name', 'Business / customer name'
        CONTACT_PERSON = 'contact_person', 'Contact person'
        MOBILE = 'mobile', 'Mobile / WhatsApp number'
        BUSINESS_TYPE = 'business_type', 'Business type (dropdown)'
        DELIVERY_LOCATION = 'delivery_location', 'Delivery location'
        DELIVERY_DATE = 'delivery_date', 'Delivery date'
        REQUIRED_PRODUCTS = 'required_products', 'Required products'
        QUANTITY = 'quantity', 'Approx quantity'
        MESSAGE = 'message', 'Additional message'

    key = models.CharField('Field', max_length=30, choices=Key.choices, unique=True)
    label = models.CharField('Label', max_length=200)
    placeholder = models.CharField('Placeholder', max_length=200, blank=True)
    icon = models.CharField('Icon', max_length=60, blank=True, help_text=ICON_HELP)
    is_required = models.BooleanField(
        'Required', default=True,
        help_text='Mobile number is always required, so the team can reply',
    )

    class Meta(OrderedItem.Meta):
        verbose_name = 'Enquiry form field'
        verbose_name_plural = 'Enquiry form fields'

    def __str__(self):
        return self.get_key_display()


class BusinessTypeOption(OrderedItem):
    """Options in the "வணிக வகை (Business Type)" dropdown."""

    name = models.CharField('Option', max_length=150, unique=True)

    class Meta(OrderedItem.Meta):
        verbose_name = 'Business type option'
        verbose_name_plural = 'Business type options'

    def __str__(self):
        return self.name


# ------------------------------------------------------------
# SECTION 6: ENQUIRY SUBMISSIONS (filled in by website visitors)
# ------------------------------------------------------------
def enquiry_file_storage():
    # "raw" resource type keeps any file format (PDF, Excel, images...) with its extension
    from cloudinary_storage.storage import RawMediaCloudinaryStorage
    return RawMediaCloudinaryStorage()


class Enquiry(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        CONTACTED = 'contacted', 'Contacted'
        QUOTED = 'quoted', 'Quotation sent'
        CONFIRMED = 'confirmed', 'Order confirmed'
        CLOSED = 'closed', 'Closed'

    business_name = models.CharField('Business / customer name', max_length=150, blank=True)
    contact_person = models.CharField('Contact person', max_length=100, blank=True)
    mobile = models.CharField('Mobile / WhatsApp', max_length=10)
    business_type = models.CharField('Business type', max_length=150, blank=True)
    delivery_location = models.CharField('Delivery location', max_length=300, blank=True)
    delivery_date = models.DateField('Delivery date', blank=True, null=True)
    required_products = models.TextField('Required products', max_length=2000, blank=True)
    quantity = models.CharField('Approx quantity', max_length=200, blank=True)
    message = models.TextField('Additional message', max_length=2000, blank=True)

    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField('Admin notes', blank=True, help_text='Internal notes, not shown to the customer')
    created_at = models.DateTimeField('Received at', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Enquiry'
        verbose_name_plural = 'Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        name = self.business_name or self.contact_person or self.mobile
        return f'{name} ({self.created_at:%d-%m-%Y})' if self.created_at else name

    @property
    def whatsapp_number(self):
        """Customer number in wa.me format (India +91)."""
        return f'91{self.mobile}'


class EnquiryFile(models.Model):
    """Uploaded requirement list: PDF, Excel, image, screenshot, etc."""

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='files')
    file = models.FileField('File', upload_to='ooruzhavan/enquiries/', storage=enquiry_file_storage)
    original_name = models.CharField('Original file name', max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Uploaded file'
        verbose_name_plural = 'Uploaded files'

    def __str__(self):
        return self.original_name or self.file.name


# ------------------------------------------------------------
# SECTION 7: WHY CHOOSE US (id="about")
# ------------------------------------------------------------
class WhyUsSection(SingletonModel):
    badge_icon = models.CharField('Badge icon', max_length=60, blank=True, help_text=ICON_HELP)
    badge_text = models.CharField('Badge text', max_length=100, blank=True)
    title = models.CharField('Heading', max_length=200)
    description = models.TextField('Description', blank=True)

    is_active = models.BooleanField('Show on website', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Why us section (About)'
        verbose_name_plural = 'Why us section (About)'

    def __str__(self):
        return 'Why us section'


class WhyUsPoint(OrderedItem):
    icon = models.CharField('Icon', max_length=60, help_text=ICON_HELP)
    title = models.CharField('Title', max_length=150)
    description = models.TextField('Description')

    class Meta(OrderedItem.Meta):
        verbose_name = 'Why us point'
        verbose_name_plural = 'Why us points'

    def __str__(self):
        return self.title


# ------------------------------------------------------------
# SECTION 8: FOOTER (id="contact")
# Logo, name, tagline, phone, email and WhatsApp number come from Site settings.
# Quick links come from Navigation menu items.
# ------------------------------------------------------------
class FooterSection(SingletonModel):
    # Column 1: brand
    description = models.TextField('About text (under logo)', blank=True)

    # Column 2: quick links
    quick_links_title = models.CharField('Quick links heading', max_length=100)

    # Column 3: contact
    contact_title = models.CharField('Contact heading', max_length=100)
    address = models.TextField('Address', blank=True, help_text='Line breaks are kept')
    service_note = models.CharField('Service hours note', max_length=150, blank=True, help_text='e.g. "24/7 திருமண ஆர்டர் சேவை"')

    # Column 4: social + WhatsApp
    social_title = models.CharField('Social heading', max_length=100)
    whatsapp_button_text = models.CharField('WhatsApp button text', max_length=100)
    whatsapp_message = models.TextField(
        'WhatsApp button message', blank=True,
        help_text='Leave empty to use the default WhatsApp message from Site settings',
    )

    # Bottom bar
    copyright_text = models.CharField(
        'Copyright text', max_length=255,
        help_text='Write {year} for the current year, updated automatically',
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Footer'
        verbose_name_plural = 'Footer'

    def __str__(self):
        return 'Footer'

    @property
    def copyright_display(self):
        from django.utils import timezone
        return self.copyright_text.replace('{year}', str(timezone.localdate().year))


class SocialLink(OrderedItem):
    name = models.CharField('Platform', max_length=50, help_text='e.g. Facebook')
    icon = models.CharField('Icon', max_length=60, help_text=ICON_HELP)
    url = models.URLField('Profile link')

    class Meta(OrderedItem.Meta):
        verbose_name = 'Social media link'
        verbose_name_plural = 'Social media links'

    def __str__(self):
        return self.name


class FooterBottomItem(OrderedItem):
    """Right side of the bottom bar: புதிய பொருட்கள் | மொத்த விலை | ..."""

    text = models.CharField('Text', max_length=100)

    class Meta(OrderedItem.Meta):
        verbose_name = 'Footer bottom item'
        verbose_name_plural = 'Footer bottom items'

    def __str__(self):
        return self.text
