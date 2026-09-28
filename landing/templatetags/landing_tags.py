from django import template

register = template.Library()


@register.filter
def cld(image, width=None):
    """
    Cloudinary image URL with automatic format + quality (and optional width).

        {{ site.logo|cld:96 }}  ->  .../image/upload/f_auto,q_auto,w_96/...
    """
    if not image:
        return ''
    url = image.url
    marker = '/image/upload/'
    if marker not in url:
        return url
    transform = 'f_auto,q_auto' + (f',w_{int(width)}' if width else '')
    return url.replace(marker, f'{marker}{transform}/', 1)


@register.filter
def cld_logo(image, size=96):
    """
    Logo for the round badge: trims plain background around the artwork,
    adds a small margin and pads to a square, so any uploaded logo fits the circle.
    """
    if not image:
        return ''
    url = image.url
    marker = '/image/upload/'
    if marker not in url:
        return url
    transform = f'e_trim/bo_50px_solid_black/c_pad,ar_1:1,b_black,w_{int(size)}/f_auto,q_auto'
    return url.replace(marker, f'{marker}{transform}/', 1)
