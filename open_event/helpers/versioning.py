import itertools

import diff_match_patch
import re


def remove_line_breaks(target_string):
    return str(target_string).replace('\r', '')

def strip_line_breaks(target_string):
    return str(target_string).replace('\n', '').replace('\r', '')


def side_by_side_diff(old_text, new_text):
    """
    Calculates a side-by-side line-based difference view.

    Wraps insertions in <ins></ins> and deletions in <del></del>.

    From: http://code.activestate.com/recipes/577784-line-based-side-by-side-diff/
    """
    old_text = str(old_text)
    new_text = str(new_text)

    def yield_open_entry(open_entry):
        """ Yield all open changes. """
        ls, rs = open_entry
        # Get unchanged parts onto the right line
        if ls[0] == rs[0]:
            yield (False, ls[0], rs[0])
            for l, r in itertools.izip_longest(ls[1:], rs[1:]):
                yield (True, l, r)
        elif ls[-1] == rs[-1]:
            for l, r in itertools.izip_longest(ls[:-1], rs[:-1]):
                yield (l != r, l, r)
            yield (False, ls[-1], rs[-1])
        else:
            for l, r in itertools.izip_longest(ls, rs):
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
                ls[-1] = ls[-1] + line
                rs[-1] = rs[-1] + line
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
