"""
Wholesale enquiry form: server-side validation for every field and every uploaded file.

Labels, placeholders and required flags come from EnquiryFormField (admin).
Error messages are in Tamil because they are shown to website visitors.
"""

import re
import unicodedata
from datetime import timedelta
from pathlib import Path

from django import forms
from django.core.validators import MaxLengthValidator
from django.utils import timezone

from .models import BusinessTypeOption, Enquiry, EnquiryFormField, EnquirySection

# ------------------------------------------------------------
# FILE RULES
# ------------------------------------------------------------
# extension -> check on the first bytes, so a renamed .exe cannot pass as .pdf
ZIP = (b'PK\x03\x04',)
OLE = (b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',)  # old .xls / .doc
ALLOWED_FILES = {
    'pdf': (b'%PDF',),
    'jpg': (b'\xff\xd8\xff',),
    'jpeg': (b'\xff\xd8\xff',),
    'png': (b'\x89PNG\r\n\x1a\n',),
    'gif': (b'GIF87a', b'GIF89a'),
    'webp': 'webp',
    'heic': 'heic',
    'heif': 'heic',
    'xlsx': ZIP,
    'xls': OLE,
    'docx': ZIP,
    'doc': OLE,
    'csv': 'text',
    'txt': 'text',
}
ALLOWED_LABEL = 'PDF, படம் (JPG, PNG, WEBP, HEIC), Excel (XLS, XLSX, CSV), Word (DOC, DOCX)'


def file_content_matches(ext, head):
    rule = ALLOWED_FILES[ext]
    if rule == 'webp':
        return head[:4] == b'RIFF' and head[8:12] == b'WEBP'
    if rule == 'heic':
        return head[4:8] == b'ftyp' and head[8:12] in (b'heic', b'heix', b'mif1', b'msf1', b'hevc')
    if rule == 'text':
        if b'\x00' in head:
            return False
        for encoding in ('utf-8', 'utf-16', 'cp1252'):
            try:
                head.decode(encoding)
                return True
            except UnicodeDecodeError:
                continue
        return False
    return head.startswith(rule)


# ------------------------------------------------------------
# TEXT RULES
# ------------------------------------------------------------
URL_PATTERN = re.compile(r'(https?://|www\.|\.com\b|\.in\b|\.net\b|<[^>]+>)', re.IGNORECASE)
MOBILE_PATTERN = re.compile(r'^[6-9]\d{9}$')


def clean_text(value):
    """Trim and collapse repeated spaces; keep line breaks for long text."""
    lines = [' '.join(line.split()) for line in (value or '').splitlines()]
    return '\n'.join(line for line in lines if line).strip()


def has_letter(value):
    return any(unicodedata.category(ch).startswith('L') for ch in value)


def is_name_text(value):
    """Letters (Tamil / English), Tamil vowel signs, spaces, dot, hyphen, apostrophe."""
    for ch in value:
        category = unicodedata.category(ch)
        if category.startswith('L') or category.startswith('M') or ch in " .-'":
            continue
        return False
    return True


# ------------------------------------------------------------
# FORM
# ------------------------------------------------------------
class EnquiryForm(forms.ModelForm):
    # Honeypot: hidden on the page. Real visitors leave it empty, bots fill it.
    website = forms.CharField(required=False)

    class Meta:
        model = Enquiry
        fields = [
            'business_name', 'contact_person', 'mobile', 'business_type', 'delivery_location',
            'delivery_date', 'required_products', 'quantity', 'message',
        ]

    # min length, max length for text fields
    LENGTHS = {
        'business_name': (2, 150),
        'contact_person': (2, 100),
        'delivery_location': (5, 300),
        'required_products': (2, 2000),
        'quantity': (1, 200),
        'message': (0, 2000),
    }

    def __init__(self, *args, files_list=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.files_list = files_list or []
        self.section = EnquirySection.load()
        self.config = {f.key: f for f in EnquiryFormField.objects.all()}

        # mobile is always a CharField here so we can accept "+91 98765 43210" and normalise it
        self.fields['mobile'] = forms.CharField(max_length=20)
        self.fields['business_type'] = forms.CharField(max_length=150, required=False)
        self.fields['delivery_date'] = forms.DateField(required=False, input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'])

        for name, field in self.fields.items():
            if name == 'website':
                continue
            cfg = self.config.get(name)
            active = cfg is None or cfg.is_active
            field.required = name == 'mobile' or (active and cfg is not None and cfg.is_required)
            field.label = cfg.label if cfg else field.label
            field.error_messages['required'] = f'{self.short_label(name)} கட்டாயம் நிரப்ப வேண்டும்.'
            field.error_messages['invalid'] = f'{self.short_label(name)} சரியாக இல்லை.'

        # Length limits are checked in _check_text with Tamil messages, not Django's English default
        for name in self.LENGTHS:
            field = self.fields[name]
            field.max_length = None
            field.validators = [v for v in field.validators if not isinstance(v, MaxLengthValidator)]
            field.widget.attrs['maxlength'] = self.LENGTHS[name][1]

        # With an uploaded list, typing products is optional
        if self.files_list:
            self.fields['required_products'].required = False

    def short_label(self, name):
        """ "வணிக வகை (Business Type)" -> "வணிக வகை" """
        cfg = self.config.get(name)
        label = cfg.label if cfg else self.fields[name].label or name
        return label.split(' (')[0].strip()

    # ---------- generic text checks ----------
    def _check_text(self, name, value, allow_urls=False):
        value = clean_text(value)
        if not value:
            return value
        min_len, max_len = self.LENGTHS[name]
        label = self.short_label(name)
        if len(value) < min_len:
            raise forms.ValidationError(f'{label} குறைந்தது {min_len} எழுத்துகள் இருக்க வேண்டும்.')
        if len(value) > max_len:
            raise forms.ValidationError(f'{label} அதிகபட்சம் {max_len} எழுத்துகள் மட்டுமே.')
        if not allow_urls and URL_PATTERN.search(value):
            raise forms.ValidationError(f'{label} பகுதியில் இணைய முகவரி (link) அனுமதிக்கப்படாது.')
        return value

    # ---------- field checks ----------
    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Invalid submission.')
        return ''

    def clean_business_name(self):
        value = self._check_text('business_name', self.cleaned_data.get('business_name'))
        if value and not has_letter(value):
            raise forms.ValidationError('வணிகப் பெயரில் எழுத்துகள் இருக்க வேண்டும்.')
        return value

    def clean_contact_person(self):
        value = self._check_text('contact_person', self.cleaned_data.get('contact_person'))
        if value and not (has_letter(value) and is_name_text(value)):
            raise forms.ValidationError('பெயரில் எழுத்துகள் மட்டுமே இருக்க வேண்டும் (எண்கள் / குறியீடுகள் வேண்டாம்).')
        return value

    def clean_mobile(self):
        digits = re.sub(r'\D', '', self.cleaned_data.get('mobile') or '')
        if len(digits) == 12 and digits.startswith('91'):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith('0'):
            digits = digits[1:]
        if not MOBILE_PATTERN.match(digits):
            raise forms.ValidationError('சரியான 10 இலக்க மொபைல் எண்ணை உள்ளிடவும் (6, 7, 8 அல்லது 9-ல் தொடங்க வேண்டும்).')
        if len(set(digits)) == 1:
            raise forms.ValidationError('சரியான மொபைல் எண்ணை உள்ளிடவும்.')
        return digits

    def clean_business_type(self):
        value = clean_text(self.cleaned_data.get('business_type'))
        if not value:
            return value
        options = set(BusinessTypeOption.objects.filter(is_active=True).values_list('name', flat=True))
        if value not in options:
            raise forms.ValidationError('பட்டியலில் உள்ள வணிக வகையைத் தேர்ந்தெடுக்கவும்.')
        return value

    def clean_delivery_location(self):
        value = self._check_text('delivery_location', self.cleaned_data.get('delivery_location'))
        if value and not has_letter(value):
            raise forms.ValidationError('சரியான விநியோக முகவரியை உள்ளிடவும்.')
        return value

    def clean_delivery_date(self):
        value = self.cleaned_data.get('delivery_date')
        if not value:
            return value
        today = timezone.localdate()
        if value < today:
            raise forms.ValidationError('விநியோக தேதி இன்று அல்லது அதற்குப் பிறகு இருக்க வேண்டும்.')
        if value > today + timedelta(days=365):
            raise forms.ValidationError('விநியோக தேதி ஒரு வருடத்திற்குள் இருக்க வேண்டும்.')
        return value

    def clean_required_products(self):
        value = self._check_text('required_products', self.cleaned_data.get('required_products'))
        if value and not has_letter(value):
            raise forms.ValidationError('தேவையான பொருட்களின் பெயர்களை உள்ளிடவும்.')
        return value

    def clean_quantity(self):
        value = self._check_text('quantity', self.cleaned_data.get('quantity'))
        if value and not re.search(r'\d', value):
            raise forms.ValidationError('அளவை எண்ணுடன் குறிப்பிடவும் (எ.கா. 50 kg, 10 மூட்டை).')
        return value

    def clean_message(self):
        return self._check_text('message', self.cleaned_data.get('message'))

    # ---------- files + cross-field checks ----------
    def clean(self):
        cleaned = super().clean()
        self._validate_files()

        # Need either typed products or an uploaded list
        products_cfg = self.config.get('required_products')
        products_needed = products_cfg is None or (products_cfg.is_active and products_cfg.is_required)
        if products_needed and not cleaned.get('required_products') and not self.files_list \
                and 'required_products' not in self.errors:
            self.add_error('required_products', 'தேவையான பொருட்களை உள்ளிடவும் அல்லது பட்டியல் கோப்பை பதிவேற்றவும்.')
        return cleaned

    def _validate_files(self):
        max_files = self.section.max_files
        max_bytes = self.section.max_file_size_mb * 1024 * 1024

        if len(self.files_list) > max_files:
            self.add_error(None, f'அதிகபட்சம் {max_files} கோப்புகள் மட்டுமே பதிவேற்றலாம்.')
            return

        for upload in self.files_list:
            name = Path(upload.name).name
            ext = Path(name).suffix.lower().lstrip('.')
            if ext not in ALLOWED_FILES:
                self.add_error(None, f'"{name}" - இந்த வகை கோப்பு அனுமதிக்கப்படாது. அனுமதிக்கப்பட்டவை: {ALLOWED_LABEL}.')
                continue
            if upload.size == 0:
                self.add_error(None, f'"{name}" - கோப்பு காலியாக உள்ளது.')
                continue
            if upload.size > max_bytes:
                self.add_error(None, f'"{name}" - கோப்பின் அளவு {self.section.max_file_size_mb} MB-க்கு மேல் இருக்கக்கூடாது.')
                continue
            upload.seek(0)
            head = upload.read(32)
            upload.seek(0)
            if not file_content_matches(ext, head):
                self.add_error(None, f'"{name}" - கோப்பு சேதமடைந்துள்ளது அல்லது அதன் வகை பெயருடன் பொருந்தவில்லை.')
