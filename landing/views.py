from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ALLOWED_FILES, EnquiryForm
from .models import (
    BusinessTypeOption,
    CustomerSection,
    CustomerType,
    EnquiryFile,
    EnquiryFormField,
    EnquirySection,
    FeaturedProduct,
    FeaturedProductSection,
    FooterBottomItem,
    FooterSection,
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


# ------------------------------------------------------------
# LANDING PAGE
# ------------------------------------------------------------
def index(request):
    site = SiteSettings.load()
    hero = HeroSection.load()

    context = {
        'site': site,
        'wa_default': site.whatsapp_link(),
        # Section 1: top bar + navbar
        'topbar_highlights': TopBarHighlight.objects.filter(is_active=True),
        'nav_items': NavMenuItem.objects.filter(is_active=True),
        # Section 1: hero
        'hero': hero if hero.is_active else None,
        'hero_features': hero.features.filter(is_active=True),
        'hero_wa': site.whatsapp_link(hero.primary_button_whatsapp_message),
    }

    # Section 2: product categories
    product_section = ProductSection.load()
    if product_section.is_active:
        categories = list(ProductCategory.objects.filter(is_active=True))
        for category in categories:
            category.button_label = category.button_text or product_section.default_button_text
            category.whatsapp_url = site.whatsapp_link(category.whatsapp_message_text)
        context.update(product_section=product_section, categories=categories)

    # Section 3: who we serve
    customer_section = CustomerSection.load()
    if customer_section.is_active:
        context.update(
            customer_section=customer_section,
            customer_types=CustomerType.objects.filter(is_active=True),
        )

    # Section 4: how it works (step numbers come from display order)
    process_section = ProcessSection.load()
    if process_section.is_active:
        context.update(
            process_section=process_section,
            process_steps=ProcessStep.objects.filter(is_active=True),
        )

    # Section 5: featured products (carousel)
    featured_section = FeaturedProductSection.load()
    if featured_section.is_active:
        featured_products = list(FeaturedProduct.objects.filter(is_active=True))
        for product in featured_products:
            product.whatsapp_url = site.whatsapp_link(product.whatsapp_message_text)
        context.update(featured_section=featured_section, featured_products=featured_products)

    # Section 6: bulk order / wholesale enquiry form
    enquiry_section = EnquirySection.load()
    if enquiry_section.is_active:
        context.update(
            enquiry_section=enquiry_section,
            enquiry_points=enquiry_section.points.filter(is_active=True),
            enquiry_fields=EnquiryFormField.objects.filter(is_active=True),
            business_types=BusinessTypeOption.objects.filter(is_active=True),
            enquiry_whatsapp_url=site.whatsapp_link(enquiry_section.whatsapp_message),
            upload_accept=','.join('.' + ext for ext in ALLOWED_FILES) + ',image/*',
            upload_extensions=','.join(ALLOWED_FILES),
            today=timezone.localdate().isoformat(),
            max_date=(timezone.localdate() + timedelta(days=365)).isoformat(),
        )

    # Section 7: why choose us
    why_us_section = WhyUsSection.load()
    if why_us_section.is_active:
        context.update(
            why_us_section=why_us_section,
            why_us_points=WhyUsPoint.objects.filter(is_active=True),
        )

    # Section 8: footer (quick links reuse the nav menu items)
    footer = FooterSection.load()
    context.update(
        footer=footer,
        footer_whatsapp_url=site.whatsapp_link(footer.whatsapp_message),
        social_links=SocialLink.objects.filter(is_active=True),
        footer_bottom_items=FooterBottomItem.objects.filter(is_active=True),
    )

    return render(request, 'landing/index.html', context)


# ------------------------------------------------------------
# ENQUIRY FORM SUBMIT
# ------------------------------------------------------------
# Max enquiries per visitor IP in the time window (basic spam protection)
RATE_LIMIT = 5
RATE_WINDOW_SECONDS = 10 * 60


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')


def build_whatsapp_summary(enquiry, form):
    """Tamil summary of the enquiry, using the same labels as the form."""
    lines = [f'வணக்கம் {SiteSettings.load().site_name}! புதிய மொத்த விலை விசாரணை (#{enquiry.pk})', '']
    for key in EnquiryFormField.Key.values:
        value = getattr(enquiry, key)
        if not value:
            continue
        if key == 'delivery_date':
            value = value.strftime('%d-%m-%Y')
        lines.append(f'{form.short_label(key)}: {value}')
    file_count = enquiry.files.count()
    if file_count:
        lines.append(f'பதிவேற்றிய கோப்புகள்: {file_count}')
    return '\n'.join(lines)


@require_POST
def submit_enquiry(request):
    section = EnquirySection.load()
    if not section.is_active:
        return JsonResponse({'ok': False, 'errors': {'__all__': ['இந்தப் படிவம் தற்போது கிடைக்கவில்லை.']}}, status=403)

    rate_key = f'enquiry-rate:{client_ip(request)}'
    if cache.get(rate_key, 0) >= RATE_LIMIT:
        return JsonResponse(
            {'ok': False, 'errors': {'__all__': ['பல முறை சமர்ப்பிக்கப்பட்டது. சில நிமிடங்கள் கழித்து முயற்சிக்கவும்.']}},
            status=429,
        )

    files = request.FILES.getlist('files')
    form = EnquiryForm(request.POST, files_list=files)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors.get_json_data()}, status=400)

    with transaction.atomic():
        enquiry = form.save()
        for upload in files:
            EnquiryFile.objects.create(enquiry=enquiry, file=upload, original_name=upload.name[:255])

    cache.set(rate_key, cache.get(rate_key, 0) + 1, RATE_WINDOW_SECONDS)

    response = {'ok': True, 'message': section.success_message}
    if section.open_whatsapp_after_submit:
        response['whatsapp_url'] = SiteSettings.load().whatsapp_link(build_whatsapp_summary(enquiry, form))
    return JsonResponse(response)
