# Regex Search for Anki 2.1
#
# Copyright: 2020 Hikaru Y. <hkrysg@gmail.com>
# Copyright: Ankitects Pty Ltd and contributors
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import re
import sre_constants
import unicodedata
from typing import Optional
from aqt import mw
from anki.utils import ids2str, splitFields
from anki.find import Finder
from anki.hooks import wrap


conf = mw.addonManager.getConfig(__name__)
wildcard = conf.get('wildcard matching on field names')
WILDCARD_ENABLED = wildcard.get('enabled')
WILDCARD_CHAR = wildcard.get('character')


def generate_pattern(expr, ignore_case=False):
    flag = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(expr, flag)
    return pattern


def _findText_wrapper(self, val, args, _old) -> str:
    match = re.fullmatch(r'/(.+)/(i?)', val)
    if match:
        pattern = generate_pattern(match.group(1), match.group(2))
        note_ids = []
        for (nid, sfld, flds) in mw.col.db.execute(
                'select id, sfld, flds from notes'):
            # See anki/pylib/anki/utils.py > joinFields(), splitFields()
            # Replace "0x1f" character with "\n"
            # to prevent ".*" from matching across fields.
            # Since sfld (also flds?) may be an integer value,
            # it must be converted with str().
            flds = str(flds).replace('\x1f', '\n')
            try:
                if pattern.search(str(sfld)) or pattern.search(flds):
                    note_ids.append(nid)
            except sre_constants.error:
                return None
        if not note_ids:
            return '0'
        return f'n.id in {ids2str(note_ids)}'
    else:
        return _old(self, val, args)


def _findField_wrapper(self, field, val, _old) -> Optional[str]:
    match = re.fullmatch(r'/(.+)/(i?)', val)

    if not((WILDCARD_CHAR in field) or match):
        return _old(self, field, val)

    if WILDCARD_ENABLED and (WILDCARD_CHAR in field):
        fields = []
        re_field = field.replace(WILDCARD_CHAR, '.*')
        has_wildcard = True
    else:
        has_wildcard = False

    if has_wildcard and not match:
        for m in mw.col.models.all():
            for f in m['flds']:
                norm_fld = unicodedata.normalize('NFC', f['name'].lower())
                if re.fullmatch(re_field, norm_fld, re.IGNORECASE):
                    fields.append(f['name'])
        if not fields:
            # wildcard pattern doesn't match any field names
            return None
        else:
            ret_list = []
            for f in fields:
                ret_list.append(f'({_old(self, f, val)})')
            return ' or '.join(ret_list)

    if match:
        # If search term is regex
        pattern = generate_pattern(match.group(1), match.group(2))

        # find models that have that field
        models = {}
        for mdl in mw.col.models.all():
            f_ords = []
            for f in mdl['flds']:
                norm_fld = unicodedata.normalize('NFC', f['name'].lower())
                if has_wildcard and re.fullmatch(
                        re_field, norm_fld, re.IGNORECASE):
                    models.setdefault(str(mdl['id']))
                    f_ords.append(f['ord'])
                elif not has_wildcard and norm_fld == field.lower():
                    models.setdefault(str(mdl['id']))
                    f_ords.append(f['ord'])
            if f_ords:
                # print(f_ords)
                models[str(mdl['id'])] = f_ords

        if not models:
            # nothing has that field
            return None

        # gather note ids
        note_ids = []
        mids = ids2str(models.keys())
        for (nid, mid, flds) in mw.col.db.execute(
                f'select id, mid, flds from notes where mid in {mids}'):
            flds = splitFields(flds)
            ordinals = models[str(mid)]
            for i in ordinals:
                field_content = flds[i]
                try:
                    if pattern.search(field_content):
                        note_ids.append(nid)
                        break
                except sre_constants.error:
                    return None

        if not note_ids:
            return '0'

        return f'n.id in {ids2str(note_ids)}'


Finder._findText = wrap(Finder._findText, _findText_wrapper, 'around')
Finder._findField = wrap(Finder._findField, _findField_wrapper, 'around')


# # For debugging
# def where_wrapper(*args, _old):
#     # for debugging
#     val = _old(*args)
#     print(f'{args=}\n{val=}')
#     return val
#
# Finder._where = wrap(Finder._where, where_wrapper, 'around')
