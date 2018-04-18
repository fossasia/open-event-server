import re
import unicodedata

import bleach
import diff_match_patch
from bleach.callbacks import target_blank, nofollow
from itertools import zip_longest


def remove_line_breaks(target_string):
    return target_string.replace('\r', '')


def strip_line_breaks(target_string):
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
        'strike'
    ]
    attrs = {
        '*': ['style']
    }
    styles = ['text-align', 'font-weight', 'text-decoration']
    cleaned = bleach.clean(html, tags=tags, attributes=attrs, styles=styles, strip=True)
    return bleach.linkify(cleaned, callbacks=[nofollow, target_blank], parse_email=True)


def strip_tags(html):
    if html is None:
        return None
    return bleach.clean(html, tags=[], attributes={}, styles=[], strip=True)


def side_by_side_diff(old_text, new_text):
    """
    Calculates a side-by-side line-based difference view.

    Wraps insertions in <ins></ins> and deletions in <del></del>.

    From: http://code.activestate.com/recipes/577784-line-based-side-by-side-diff/
    """

    if not old_text:
        old_text = ''

    if not new_text:
        new_text = ''

    old_text = strip_tags(strip_line_breaks(str(old_text).encode('utf-8', errors='ignore')))
    new_text = strip_tags(strip_line_breaks(str(new_text).encode('utf-8', errors='ignore')))

    old_text = unicodedata.normalize("NFKD", old_text)
    new_text = unicodedata.normalize("NFKD", new_text)

    def yield_open_entry(open_entry):
        """ Yield all open changes. """
        ls, rs = open_entry
        # Get unchanged parts onto the right line
        if ls[0] == rs[0]:
            yield (False, ls[0], rs[0])
            for l, r in zip_longest(ls[1:], rs[1:]):
                yield (True, l, r)
        elif ls[-1] == rs[-1]:
            for l, r in zip_longest(ls[:-1], rs[:-1]):
                yield (l != r, l, r)
            yield (False, ls[-1], rs[-1])
        else:
            for l, r in zip_longest(ls, rs):
                yield (True, l, r)

    line_split = re.compile(r'(?:\r?\n)')
    dmp = diff_match_patch.diff_match_patch()

    diff = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diff)

    open_entry = ([None], [None])
    for change_type, entry in diff:
        assert change_type in [-1, 0, 1]

        entry = (entry.replace('&', '&amp;')
                 .replace('<', '&lt;')
                 .replace('>', '&gt;'))

        lines = line_split.split(entry)

        # Merge with previous entry if still open
        ls, rs = open_entry

        line = lines[0]
        if line:
            if change_type == 0:
                ls[-1] = ls[-1] or ''
                rs[-1] = rs[-1] or ''
                ls[-1] += line
                rs[-1] += line
            elif change_type == 1:
                rs[-1] = rs[-1] or ''
                rs[-1] += '<ins>%s</ins>' % line if line else ''
            elif change_type == -1:
                ls[-1] = ls[-1] or ''
                ls[-1] += '<del>%s</del>' % line if line else ''

        lines = lines[1:]

        if lines:
            if change_type == 0:
                # Push out open entry
                for entry in yield_open_entry(open_entry):
                    yield entry

                # Directly push out lines until last
                for line in lines[:-1]:
                    yield (False, line, line)

                # Keep last line open
                open_entry = ([lines[-1]], [lines[-1]])
            elif change_type == 1:
                ls, rs = open_entry

                for line in lines:
                    rs.append('<ins>%s</ins>' % line if line else '')

                open_entry = (ls, rs)
            elif change_type == -1:
                ls, rs = open_entry

                for line in lines:
                    ls.append('<del>%s</del>' % line if line else '')

                open_entry = (ls, rs)

    # Push out open entry
    for entry in yield_open_entry(open_entry):
        yield entry
