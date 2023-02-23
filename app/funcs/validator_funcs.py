import re
from datetime import date
import phonenumbers
import probablepeople as pp
from nameparser import HumanName
from collections import namedtuple

PersonName = namedtuple(
    'PersonName',
    [
        'title',
        'firstname',
        'lastname',
        'middlename',
        'suffix',
        'prefix',
        'formatted',
        'deceased'
    ]
)


def format_dates(v):
    if v:
        return date(int(v[:4]), int(v[4:6]), int(v[6:8]))


def strip_nonwhitespace(v):
    return re.sub('\\s+', ' ', v)


def strip_punctuation(v):
    return re.sub('\\W+', '', v)


def zip_validator(zipcode):
    _zipcode = str(zipcode)
    _zip5, _zip4 = None, None
    if len(_zipcode) == 5:
        _zip5 = _zipcode
    elif '-' in _zipcode:
        _zip_split = _zipcode.split('-')
        _zip5 = _zip_split[0]
        _zip4 = _zip_split[1]

    elif not _zipcode.isnumeric():
        if len(_zipcode) == 5:
            _zip5 = _zipcode
    else:
        raise ValueError('Invalid Zip Code')

    return _zip5, _zip4


def phone_validator(phone):
    try:
        _phone = phonenumbers.parse(phone, 'US')
        if phonenumbers.is_valid_number(_phone):
            return phonenumbers.format_number(_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
    except phonenumbers.phonenumberutil.NumberParseException:
        return None


def name_parser(
        key_to_parse: str) -> PersonName:
    filer_name = key_to_parse
    if filer_name:
        details = pp.parse(filer_name)

        if 'GivenName' in [x[1] for x in details]:
            pfx = re.findall(r"(?<=\()(.*?)(?=\))", filer_name)

            if 'DECEASED' in pfx:
                name_deceased = True
                pfx.pop(pfx.index('DECEASED'))
            else:
                name_deceased = False

            person_split = HumanName(filer_name)
            name_title = person_split.title
            name_first = person_split.first
            name_last = person_split.last
            name_middle = strip_punctuation(
                person_split.middle
            ) if person_split.middle else None
            name_suffix = strip_punctuation(
                person_split.suffix
            ).replace('.', '') if person_split.suffix else None

            if person_split.nickname or pfx:
                pfx = ' '.join(pfx)
                name_fmt = strip_nonwhitespace(' '.join(
                    [
                        pfx,
                        person_split.first,
                        person_split.middle,
                        person_split.last
                    ]
                ))
            elif person_split.title:
                pfx = person_split.title
                name_fmt = strip_nonwhitespace(
                    ' '.join(
                        [
                            person_split.title,
                            person_split.first,
                            person_split.middle,
                            person_split.last,
                            person_split.suffix
                        ]
                    )
                )

            else:
                pfx = None
                name_fmt = strip_nonwhitespace(
                    ' '.join(
                        [
                            person_split.first,
                            person_split.middle,
                            person_split.last,
                            person_split.suffix
                        ]
                    )
                )

            _name_prefix = strip_nonwhitespace(pfx).replace('.', '') if pfx else None
            _name_formatted = strip_nonwhitespace(name_fmt.upper()) if name_fmt else None
            _deceased = name_deceased if name_deceased else None

            return PersonName(
                title=name_title,
                firstname=name_first,
                lastname=name_last,
                middlename=name_middle,
                suffix=name_suffix,
                prefix=_name_prefix,
                formatted=_name_formatted,
                deceased=name_deceased
            )
