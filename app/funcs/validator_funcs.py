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

FilerCorporationColumns = namedtuple(
    'CorporationNameColumns',
    [
        'name',
        'nameFormatted'
    ]
)

FilerPersonColumns = namedtuple(
    'FilerPersonColumns',
    [
        'name',
        'nameFormatted'
    ]
)

filer_name_cols = PersonName(
    title='filerTitle',
    firstname='filerFirstName',
    lastname='filerLastName',
    middlename='filerMiddleName',
    suffix='filerSuffix',
    prefix='filerPrefix',
    formatted=None,
    deceased=None
)

filer_corporation_cols = FilerCorporationColumns('filerCompanyName', 'filerCompanyNameFormatted')
filer_person_cols = FilerPersonColumns('filerName', 'filerNameFormatted')

payee_corporation_cols = FilerCorporationColumns('payeeCompanyName', 'payeeCompanyNameFormatted')


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


def assign_to_name_cols(v: dict, to_parse, col_names=filer_name_cols):
    _split = HumanName(to_parse)
    v[col_names.title] = _split.title
    v[col_names.firstname] = _split.first
    v[col_names.lastname] = _split.last
    v[col_names.middlename] = None if not _split.middle else strip_punctuation(_split.middle)
    v[col_names.suffix] = None if not _split.suffix else strip_punctuation(_split.suffix).replace('.', '')
    return v


def corporation_parser(v: dict, name_to_parse, corp_cols: FilerCorporationColumns = filer_corporation_cols):
    details = pp.parse(name_to_parse)
    companyname = strip_nonwhitespace(
        ' '.join([x[0] for x in details if x[1] == 'CorporationName'])
    )
    andcompany = strip_nonwhitespace(
        ' '.join([x[0] for x in details if x[1] == 'CorporationNameAndCompany'])
    )
    legaltype = strip_nonwhitespace(
        ' '.join([x[0] for x in details if x[1] == 'CorporationLegalType'])
    )

    if all([companyname, andcompany, legaltype]):
        v[corp_cols.name] = strip_nonwhitespace(
            ' '.join([companyname, andcompany])
        )
        v[corp_cols.nameFormatted] = strip_nonwhitespace(
            ' '.join([companyname, andcompany, legaltype])
        )
    elif all([companyname, andcompany]):
        v[corp_cols.name] = strip_nonwhitespace(
            ' '.join([companyname, andcompany])
        )
        v[corp_cols.nameFormatted] = strip_nonwhitespace(
            ' '.join([companyname, andcompany])
        )
    elif all([companyname, legaltype]):
        v[corp_cols.name] = companyname
        v[corp_cols.nameFormatted] = strip_nonwhitespace(
            ' '.join([companyname, legaltype])
        )
    elif companyname:
        v[corp_cols.name] = companyname
        v[corp_cols.nameFormatted] = companyname

    else:
        v[corp_cols.name] = None
        v[corp_cols.nameFormatted] = None
    return v


def name_corporation_parser(
        v: dict,
        name_to_parse: str,
        person_cols: PersonName = filer_name_cols,
        corporation_cols: FilerCorporationColumns = filer_corporation_cols):
    val = v
    details = pp.parse(name_to_parse)  # Identify type of name
    _split = HumanName(name_to_parse)

    if 'GivenName' in [x[1] for x in details]:
        # Check for prefix details that parser may have trouble identifying
        match = re.search(r"(?<=\()(.*?)(?=\))", name_to_parse)

        # Split person name into parts
        val = assign_to_name_cols(v=val, to_parse=name_to_parse, col_names=person_cols)

        # Assign name parts to respective keys

        if _split.nickname or match:
            pfx = None if not match or _split.nickname else match.group() or _split.nickname
            name_fmt = ' '.join(
                [
                    pfx,
                    _split.first,
                    _split.middle,
                    _split.last
                ]
            )
        elif _split.title:
            pfx = _split.title
            name_fmt = ' '.join(
                [
                    _split.title,
                    _split.first,
                    _split.middle,
                    _split.last,
                    _split.suffix
                ]
            )

        else:
            pfx = None
            name_fmt = ' '.join(
                [
                    _split.first,
                    _split.middle,
                    _split.last,
                    _split.suffix
                ]
            )

        val[person_cols.prefix] = strip_nonwhitespace(pfx).replace('.', '') if pfx else None
        val[person_cols.formatted] = strip_nonwhitespace(name_fmt.upper()) if name_fmt else None

    elif _split:
        val = assign_to_name_cols(
            v=val,
            to_parse=name_to_parse,
            col_names=person_cols
        )

        if _split.nickname == 'THE HONORABLE':
            pfx = _split.nickname
            name_fmt = strip_nonwhitespace(' '.join(
                [
                    pfx,
                    _split.first,
                    _split.middle,
                    _split.last
                ]
            ))
        elif _split.title:
            pfx = _split.title
            name_fmt = strip_nonwhitespace(
                ' '.join(
                    [
                        _split.title,
                        _split.first,
                        _split.middle,
                        _split.last,
                        _split.suffix
                    ]
                )
            )

        else:
            pfx = None
            name_fmt = strip_nonwhitespace(
                ' '.join(
                    [
                        _split.first,
                        _split.middle,
                        _split.last,
                        _split.suffix
                    ]
                )
            )

        val[person_cols.prefix] = strip_nonwhitespace(pfx).replace('.', '') if pfx else None
        val[person_cols.formatted] = strip_nonwhitespace(name_fmt.upper()) if name_fmt else None

    elif 'CorporationName' in [x[1] for x in details]:
        val = corporation_parser(
            v=val,
            name_to_parse=name_to_parse,
            corp_cols=corporation_cols
        )
    else:
        val[person_cols.formatted] = name_to_parse

    return val
