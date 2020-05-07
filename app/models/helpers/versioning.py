import re

import bleach
from bleach.callbacks import nofollow, target_blank


def remove_line_breaks(target_string: str) -> str:
    return target_string.replace('\r', '')


def strip_line_breaks(target_string: str) -> str:
    return target_string.replace('\n', '').replace('\r', '')


def clean_up_string(target_string):
    if target_string:
        if not re.search('[a-zA-Z]', target_string):
            return strip_line_breaks(target_string).strip().replace(" ", "")
        else:
            return remove_line_breaks(target_string).strip()
    return target_string


def clean_html(html):
    if html is None:
        return None
    tags = [
        'b',
        'strong',
        'span',
        'p',
        'em',
        'i',
        'u',
        'center',
        'sup',
        'sub',
        'ul',
        'ol',
        'li',
        'strike',
    ]
    attrs = {'*': ['style']}
    styles = ['text-align', 'font-weight', 'text-decoration']
    cleaned = bleach.clean(html, tags=tags, attributes=attrs, styles=styles, strip=True)
    return bleach.linkify(
        cleaned,
        callbacks=[nofollow, target_blank],
        parse_email=True,  # pytype: disable=wrong-arg-types
    )


def strip_tags(html):
    if html is None:
        return None
    return bleach.clean(html, tags=[], attributes={}, styles=[], strip=True)
