from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import (
    BusinessTypeOption,
    CustomerSection,
    CustomerType,
    Enquiry,
    EnquiryFile,
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

admin.site.site_header = 'ஊர் உழவன் - Admin'
admin.site.site_title = 'ஊர் உழவன் Admin'
admin.site.index_title = 'Website content'


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
class SingletonAdmin(admin.ModelAdmin):
    """Allow only one row; no delete."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


def image_preview(image, height=80):
    if image:
        return format_html('<img src="{}" style="height:{}px;border-radius:6px;" />', image.url, height)
    return '-'


# ------------------------------------------------------------
# SECTION 1: SITE SETTINGS / TOP BAR / NAVIGATION
# ------------------------------------------------------------
@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    readonly_fields = ('logo_preview', 'updated_at')
    fieldsets = (
        ('Branding', {'fields': ('site_name', 'tagline', 'logo', 'logo_preview')}),
        ('Contact details', {'fields': ('phone_number', 'email', 'location')}),
        ('Top bar labels', {'fields': ('topbar_phone_label', 'topbar_email_label')}),
        ('WhatsApp', {'fields': ('whatsapp_number', 'whatsapp_default_message')}),
        ('Header button', {'fields': ('header_cta_text', 'header_cta_icon')}),
        ('Floating buttons', {'fields': ('show_floating_whatsapp', 'show_floating_call')}),
        ('Info', {'fields': ('updated_at',)}),
    )

    @admin.display(description='Logo preview')
    def logo_preview(self, obj):
        return image_preview(obj.logo)


@admin.register(TopBarHighlight)
class TopBarHighlightAdmin(admin.ModelAdmin):
    list_display = ('text', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(NavMenuItem)
class NavMenuItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'target_section', 'order', 'is_active')
    list_editable = ('order', 'is_active')


# ------------------------------------------------------------
# SECTION 1: HERO
# ------------------------------------------------------------
class HeroFeatureInline(admin.TabularInline):
    model = HeroFeature
    extra = 0
    fields = ('icon', 'text', 'order', 'is_active')


@admin.register(HeroSection)
class HeroSectionAdmin(SingletonAdmin):
    inlines = [HeroFeatureInline]
    readonly_fields = ('background_preview', 'updated_at')
    fieldsets = (
        ('Content', {'fields': ('title', 'description')}),
        ('Background', {'fields': ('background_image', 'background_preview')}),
        ('Primary button (WhatsApp)', {
            'fields': ('primary_button_text', 'primary_button_icon', 'primary_button_whatsapp_message'),
        }),
        ('Secondary button (scroll)', {'fields': ('secondary_button_text', 'secondary_button_target')}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )

    @admin.display(description='Preview')
    def background_preview(self, obj):
        return image_preview(obj.background_image, height=160)


# ------------------------------------------------------------
# SECTION 2: PRODUCT CATEGORIES
# ------------------------------------------------------------
@admin.register(ProductSection)
class ProductSectionAdmin(SingletonAdmin):
    readonly_fields = ('description_preview', 'updated_at')
    fieldsets = (
        ('Badge', {'fields': ('badge_icon', 'badge_text')}),
        ('Content', {'fields': ('title', 'description', 'description_preview')}),
        ('Cards', {'fields': ('default_button_text',)}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )

    @admin.display(description='Description as shown on website')
    def description_preview(self, obj):
        return obj.description_display if obj.pk else '-'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'tag', 'order', 'is_active')
    list_display_links = ('thumbnail', 'name')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'tag', 'description')
    readonly_fields = ('preview',)
    fieldsets = (
        ('Category', {'fields': ('tag', 'name', 'description')}),
        ('Image', {'fields': ('image', 'preview')}),
        ('Button (WhatsApp)', {'fields': ('button_text', 'whatsapp_message')}),
        ('Display', {'fields': ('order', 'is_active')}),
    )

    @admin.display(description='Image')
    def thumbnail(self, obj):
        return image_preview(obj.image, height=40)

    @admin.display(description='Preview')
    def preview(self, obj):
        return image_preview(obj.image, height=160)


# ------------------------------------------------------------
# SECTION 3: WHO WE SERVE / B2B CUSTOMERS
# ------------------------------------------------------------
@admin.register(CustomerSection)
class CustomerSectionAdmin(SingletonAdmin):
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Badge', {'fields': ('badge_icon', 'badge_text')}),
        ('Content', {'fields': ('title', 'description')}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )


@admin.register(CustomerType)
class CustomerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'subtitle', 'highlight', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'subtitle', 'description')
    fieldsets = (
        ('Card', {'fields': ('icon', 'name', 'subtitle', 'description')}),
        ('Card footer', {'fields': ('key_point', 'highlight')}),
        ('Display', {'fields': ('order', 'is_active')}),
    )


# ------------------------------------------------------------
# SECTION 4: HOW IT WORKS / PROCESS
# ------------------------------------------------------------
@admin.register(ProcessSection)
class ProcessSectionAdmin(SingletonAdmin):
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Content', {'fields': ('title', 'description')}),
        ('Steps', {'fields': ('step_prefix',)}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ('shown_as', 'tag', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    readonly_fields = ('shown_as',)
    fieldsets = (
        ('Step', {'fields': ('icon', 'title', 'shown_as', 'description', 'tag')}),
        ('Display', {'fields': ('order', 'is_active')}),
    )

    @admin.display(description='Shown on website as')
    def shown_as(self, obj):
        number = obj.step_number if obj.pk else None
        if number is None:
            return f'(hidden) {obj.title}' if obj.pk else '-'
        return f'{ProcessSection.load().step_prefix} {number}: {obj.title}'


# ------------------------------------------------------------
# SECTION 5: FEATURED PRODUCTS
# ------------------------------------------------------------
@admin.register(FeaturedProductSection)
class FeaturedProductSectionAdmin(SingletonAdmin):
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Badge', {'fields': ('badge_icon', 'badge_text')}),
        ('Content', {'fields': ('title', 'description')}),
        ('Card button (WhatsApp)', {'fields': ('button_text', 'button_icon')}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )


@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'tag', 'order', 'is_active')
    list_display_links = ('thumbnail', 'name')
    list_editable = ('order', 'is_active')
    list_filter = ('tag', 'is_active')
    search_fields = ('name', 'tag', 'description')
    readonly_fields = ('preview',)
    fieldsets = (
        ('Product', {'fields': ('name', 'tag', 'description')}),
        ('Image', {'fields': ('image', 'preview')}),
        ('WhatsApp', {'fields': ('whatsapp_message',)}),
        ('Display', {'fields': ('order', 'is_active')}),
    )

    @admin.display(description='Image')
    def thumbnail(self, obj):
        return image_preview(obj.image, height=40)

    @admin.display(description='Preview')
    def preview(self, obj):
        return image_preview(obj.image, height=160)


# ------------------------------------------------------------
# SECTION 6: BULK ORDER / WHOLESALE ENQUIRY
# ------------------------------------------------------------
class EnquiryPanelPointInline(admin.TabularInline):
    model = EnquiryPanelPoint
    extra = 0
    fields = ('text', 'order', 'is_active')


@admin.register(EnquirySection)
class EnquirySectionAdmin(SingletonAdmin):
    inlines = [EnquiryPanelPointInline]
    readonly_fields = ('panel_preview', 'updated_at')
    fieldsets = (
        ('Left panel', {'fields': (
            'panel_image', 'panel_preview', 'panel_badge_text',
            'panel_title', 'panel_title_highlight', 'panel_description',
        )}),
        ('Form header', {'fields': ('form_title', 'form_description', 'form_badge_icon', 'form_badge_text')}),
        ('File upload box', {'fields': ('upload_icon', 'upload_title', 'upload_hint', 'max_files', 'max_file_size_mb')}),
        ('WhatsApp box', {'fields': ('whatsapp_box_title', 'whatsapp_box_text', 'whatsapp_button_text', 'whatsapp_message')}),
        ('Submit', {'fields': ('submit_button_icon', 'submit_button_text', 'success_message', 'open_whatsapp_after_submit')}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )

    @admin.display(description='Preview')
    def panel_preview(self, obj):
        return image_preview(obj.panel_image, height=200)


@admin.register(EnquiryFormField)
class EnquiryFormFieldAdmin(admin.ModelAdmin):
    """The set of fields is fixed (they map to database columns); their wording is editable."""

    list_display = ('key', 'label', 'is_required', 'order', 'is_active')
    list_editable = ('is_required', 'order', 'is_active')
    readonly_fields = ('key',)
    fields = ('key', 'label', 'placeholder', 'icon', 'is_required', 'order', 'is_active')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BusinessTypeOption)
class BusinessTypeOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active')
    list_editable = ('order', 'is_active')


# ------------------------------------------------------------
# SECTION 6: ENQUIRY SUBMISSIONS (inbox)
# ------------------------------------------------------------
class EnquiryFileInline(admin.TabularInline):
    model = EnquiryFile
    extra = 0
    fields = ('original_name', 'open_file', 'uploaded_at')
    readonly_fields = ('original_name', 'open_file', 'uploaded_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='File')
    def open_file(self, obj):
        if not obj.file:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener">Open / Download</a>', obj.file.url)


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    inlines = [EnquiryFileInline]
    list_display = (
        'created_at', 'business_name', 'contact_person', 'mobile', 'business_type',
        'delivery_date', 'file_count', 'status', 'reply_on_whatsapp',
    )
    list_display_links = ('created_at', 'business_name')
    list_editable = ('status',)
    list_filter = ('status', 'business_type', 'delivery_date', 'created_at')
    search_fields = ('business_name', 'contact_person', 'mobile', 'delivery_location', 'required_products')
    readonly_fields = (
        'business_name', 'contact_person', 'mobile', 'reply_on_whatsapp', 'business_type',
        'delivery_location', 'delivery_date', 'required_products', 'quantity', 'message',
        'created_at', 'updated_at',
    )
    fieldsets = (
        ('Customer', {'fields': ('business_name', 'contact_person', 'mobile', 'reply_on_whatsapp', 'business_type')}),
        ('Delivery', {'fields': ('delivery_location', 'delivery_date')}),
        ('Requirement', {'fields': ('required_products', 'quantity', 'message')}),
        ('Follow-up', {'fields': ('status', 'admin_notes')}),
        ('Info', {'fields': ('created_at', 'updated_at')}),
    )

    def has_add_permission(self, request):
        return False  # Enquiries only come from the website form

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_file_count=Count('files'))

    @admin.display(description='Files', ordering='_file_count')
    def file_count(self, obj):
        return obj._file_count if hasattr(obj, '_file_count') else obj.files.count()

    @admin.display(description='WhatsApp')
    def reply_on_whatsapp(self, obj):
        if not obj.mobile:
            return '-'
        return format_html(
            '<a href="https://wa.me/{}" target="_blank" rel="noopener" '
            'style="color:#128C7E;font-weight:600;">Chat</a>',
            obj.whatsapp_number,
        )


# ------------------------------------------------------------
# SECTION 7: WHY CHOOSE US
# ------------------------------------------------------------
@admin.register(WhyUsSection)
class WhyUsSectionAdmin(SingletonAdmin):
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Badge', {'fields': ('badge_icon', 'badge_text')}),
        ('Content', {'fields': ('title', 'description')}),
        ('Visibility', {'fields': ('is_active', 'updated_at')}),
    )


@admin.register(WhyUsPoint)
class WhyUsPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')
    fieldsets = (
        ('Card', {'fields': ('icon', 'title', 'description')}),
        ('Display', {'fields': ('order', 'is_active')}),
    )


# ------------------------------------------------------------
# SECTION 8: FOOTER
# ------------------------------------------------------------
@admin.register(FooterSection)
class FooterSectionAdmin(SingletonAdmin):
    readonly_fields = ('copyright_preview', 'shared_settings', 'updated_at')
    fieldsets = (
        ('Brand column', {'fields': ('description', 'shared_settings')}),
        ('Quick links column', {
            'fields': ('quick_links_title',),
            'description': 'Links are the same as Navigation menu items.',
        }),
        ('Contact column', {'fields': ('contact_title', 'address', 'service_note')}),
        ('Social + WhatsApp column', {'fields': ('social_title', 'whatsapp_button_text', 'whatsapp_message')}),
        ('Bottom bar', {'fields': ('copyright_text', 'copyright_preview')}),
        ('Info', {'fields': ('updated_at',)}),
    )

    @admin.display(description='Shown on website as')
    def copyright_preview(self, obj):
        return obj.copyright_display if obj.pk else '-'

    @admin.display(description='From Site settings')
    def shared_settings(self, obj):
        s = SiteSettings.load()
        return format_html(
            '{} · {}<br>Phone: {} · Email: {} · WhatsApp: {}<br>'
            '<a href="/admin/landing/sitesettings/1/change/">Edit in Site settings</a>',
            s.site_name, s.tagline, s.phone_number, s.email, s.whatsapp_number,
        )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(FooterBottomItem)
class FooterBottomItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'order', 'is_active')
    list_editable = ('order', 'is_active')
