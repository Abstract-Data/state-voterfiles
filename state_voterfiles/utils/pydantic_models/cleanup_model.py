from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional, Annotated, Self
from datetime import datetime, date
from functools import partial
from enum import StrEnum
import usaddress
import phonenumbers
# import logfire
from icecream import ic
from rapidfuzz import fuzz

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from state_voterfiles.utils.pydantic_models.rename_model import RecordRenamer
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
import state_voterfiles.utils.validation.default_helpers as helpers
import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.validation.election_history import StateElectionHistoryValidator
from state_voterfiles.utils.pydantic_models.field_models import (
    ValidatedPhoneNumber,
    Address,
    PersonName,
    VoterRegistration,
    VEPMatch,
    District,
    CustomFields,
    VendorTags,
    InputData,
    RecordBaseModel
)

ic.enable()
ic.configureOutput(prefix='PreValidationCleanUp| ', includeContext=True)

# TODO: Check districts to make sure they validate TODO: Remove all validation aliases so that we can use SQLModel
#  directly for the models
# TODO: Run validation on state voterfiles, specifically Texas to ensure changes made to
#   validation process in cleanup still work.

RAISE_EXCEPTIONS_FOR_CHANGES = False

AddressCorrections = Dict[str, List[str]]

NEEDED_ADDRESS_PARTS = ['address1', 'address1', 'city', 'state', 'zip5', 'zip4']

OUTPUT_ADDRESS_DICT_KEYS = ['address_parts', 'zipcode', 'county', 'standardized', 'key'] + NEEDED_ADDRESS_PARTS


class AddressType(StrEnum):
    RESIDENCE = 'residence'
    MAIL = 'mail'


AddressTypeList = [AddressType.MAIL, AddressType.RESIDENCE]


@pydantic_dataclass
class AddressValidationFuncs:
    @staticmethod
    def get_existing_parts(
            address_type_: str,
            renamed_: RecordRenamer,
            address_corrections_: List[str]) -> [helpers.AddressLinesOrdered,
                                                 helpers.AddressLinesDict,
                                                 AddressCorrections]:
        _part_field_prefix = f'{address_type_}_part'
        _existing_parts = vfuncs.getattr_with_prefix(pfx=_part_field_prefix, obj=renamed_)

        if not _existing_parts:
            return {}, {}, address_corrections_

        with_suffix = partial(vfuncs.next_with_key_suffix, dict_=_existing_parts)
        address1_parts = [with_suffix(x) for x in helpers.ADDRESS1_PREFIXES if with_suffix(x)]
        address2_parts = [with_suffix(x) for x in helpers.ADDRESS2_PREFIXES if with_suffix(x)]
        _existing_parts[f'{address_type_}_address1'] = " ".join(address1_parts) if address1_parts else None
        _existing_parts[f'{address_type_}_address2'] = " ".join(address2_parts) if address2_parts else None
        if any(_existing_parts.values()):
            existing_parts_address_lines = helpers.AddressLinesOrdered(
                address1=_existing_parts.get(f'{address_type_}_address1'),
                address2=_existing_parts.get(f'{address_type_}_address2'),
                city=_existing_parts.get(f'{_part_field_prefix}_city'),
                state=_existing_parts.get(f'{_part_field_prefix}_state'),
                zip5=_existing_parts.get(f'{_part_field_prefix}_zip5'),
                zip4=_existing_parts.get(f'{_part_field_prefix}_zip4')
            )
            if any(dict(existing_parts_address_lines).values()):
                if not existing_parts_address_lines.state and address_type_ == AddressType.RESIDENCE:
                    existing_parts_address_lines.state = renamed_.settings.get('STATE').get('abbreviation')
                    existing_parts_address_lines.model_validate(existing_parts_address_lines)

            if existing_parts_address_lines.standardized:
                existing_parts_parsed = {
                    value_: type_ for value_, type_ in usaddress.parse(
                        " ".join(
                            [
                                x for x in dict(existing_parts_address_lines).values() if x
                            ]
                        )
                    )
                }
                needed_parts = NEEDED_ADDRESS_PARTS.copy()
                address_lines_dict = {}
                if existing_parts_parsed:
                    for k, v in existing_parts_parsed.items():
                        for part in needed_parts:
                            field_dict = getattr(helpers.ADDRESS_PARSER_FIELDS, part.upper(), None)
                            if field_dict and v in field_dict:
                                address_lines_dict.setdefault(part, []).append(k)
                                address_corrections_.append(f"Added parsed fields to {part}")

                    # existing_not_parts_into_lines = helpers.AddressLinesOrdered(
                    #     **{
                    #         k: " ".join(list(v)) for k, v in address_lines_dict.items()
                    #     }
                    # )
                    return existing_parts_address_lines, existing_parts_parsed, address_corrections_
            return {}, {}, address_corrections_

    @staticmethod
    def get_existing_not_parts(renamed_: RecordRenamer, address_type_: str,
                               address_corrections_: List[str]) -> [helpers.AddressLinesOrdered,
                                                                    helpers.AddressLinesDict,
                                                                    AddressCorrections]:
        """ Get the existing full address lines of the address that are not address parts. """
        needed_parts = NEEDED_ADDRESS_PARTS.copy()

        _existing_not_parts = {k: getattr(renamed_, f'{address_type_}_{k}', None) for k in needed_parts}
        if not _existing_not_parts:
            return {}, {}, address_corrections_

        existing_address = helpers.AddressLinesOrdered(**_existing_not_parts)
        if existing_address.standardized:
            existing_address_parsed = {
                value_: type_ for value_, type_ in usaddress.parse(
                    existing_address.standardized if existing_address.standardized else ' '.join(
                        list(dict(existing_address).values())))
            }

            parse_new_parts_dict = {}
            if existing_address_parsed:
                for value_, type_ in existing_address_parsed.items():
                    parse_new_parts_dict.setdefault(type_, []).append(value_)
                # new_address_lines = {}
                address_lines_dict = {}
                needed_parts.append('usps')
                for k, v in existing_address_parsed.items():
                    if v:
                        if address_lines_dict.get(v):
                            address_lines_dict[v] += f" {k}"
                        else:
                            address_lines_dict[v] = k

                for k, v in existing_address_parsed.items():
                    for part in needed_parts:
                        field_dict = getattr(helpers.ADDRESS_PARSER_FIELDS, part.upper(), None)
                        if field_dict and v in field_dict:
                            # Check if the value is already in the list before appending
                            if k not in address_lines_dict.setdefault(part, []):
                                address_lines_dict[part].append(k)
                                address_corrections_.append(f"Added parsed fields to {part}")
                    existing_individual_parts = helpers.AddressPartsDict(**parse_new_parts_dict)
                    return existing_address, existing_individual_parts, address_corrections_
        return {}, {}, address_corrections_

    @staticmethod
    def validate_address(address_type, _renamed: RecordRenamer) -> [Dict[str, Any], Dict[str, Any]]:
        if not _renamed:
            return None, None

        match address_type:
            case 'mail' | 'mailing':
                _address_type = AddressType.MAIL
            case 'residential' | 'residence':
                _address_type = AddressType.RESIDENCE
            case _:
                raise ValueError(f"Invalid address type: {address_type}")
        corrections = []

        existing_parts_lines, existing_parts_parsed, corrections = AddressValidationFuncs.get_existing_parts(
            address_type_=address_type,
            renamed_=_renamed,
            address_corrections_=corrections
        )
        existing_address_lines, existing_address_parsed, corrections = AddressValidationFuncs.get_existing_not_parts(
            renamed_=_renamed,
            address_type_=address_type,
            address_corrections_=corrections
        )
        if all([existing_address_lines, existing_parts_lines]):
            check_dict = dict(existing_address_lines)

            for k, v in dict(existing_address_lines).items():
                if not v and (part := getattr(existing_parts_lines, k, None)):
                    check_dict[k] = part
                    corrections.append(f"Added {k} from parts to address")
        else:
            check_dict = next((x for x in [existing_address_lines, existing_parts_lines] if x), None)

        if check_dict:
            address_parts = vfuncs.safe_dict_merge(dict(existing_address_parsed), dict(existing_parts_parsed))
            new_check_dict = helpers.AddressLinesOrdered(**dict(check_dict))
            if not new_check_dict.state and address_type == AddressType.RESIDENCE:
                new_check_dict.state = _renamed.settings.get('STATE').get('abbreviation')
                new_check_dict.model_validate(new_check_dict)
            std_address = new_check_dict.standardized
            corrections.append("Standardized address based on address1, city, state, and zipcode")

            address_dict_to_return = {
                f'{address_type}_{part}': getattr(new_check_dict, part, None) for part in NEEDED_ADDRESS_PARTS
            }

            address_dict_to_return.update({
                f'{address_type}_standardized': std_address,
                f'{address_type}_key': RecordKeyGenerator(std_address).hash if std_address else None,
                f'{address_type}_address_parts': address_parts,
                f'{address_type}_is_mailing': True if address_type == AddressType.MAIL else None
            })
            if not address_dict_to_return.get(f'{address_type}_zip5'):
                corrections.append("Zip5 was missing, cannot correctly standardize address.")
                address_dict_to_return.pop(f'{address_type}_standardized', None)
                if address_dict_to_return.pop(f'{address_type}_zip4', None):
                    corrections.append("Zip4 was removed because Zip5 was missing.")
                raise PydanticCustomError(
                    'cannot_standardize',
                    'Zip5 is missing. Cannot standardize address.',
                    dict(
                        model='PreValidationCleanUp',
                        function=f'validate_{address_type}_address',
                        nested_function='validate_address'
                    )
                )
            if (address_dict_to_return.get(f'{address_type}_zip4') and
                    len(address_dict_to_return.get(f'{address_type}_zip4')) != 4):
                corrections.append("Zip4 was too short. Removed Zip4")
                address_dict_to_return[f'{address_type}_zip4'] = None

            _return_address_corrections = {address_type: list(set(corrections))}
            return address_dict_to_return, _return_address_corrections

    @staticmethod
    def copy_address(src, dest):
        """Copy address details from src to dest."""
        dest.standardized = src.standardized
        dest.address1 = src.address1
        dest.address2 = src.address2
        dest.city = src.city
        dest.state = src.state
        dest.zip5 = src.zip5
        dest.zip4 = src.zip4
        dest.zipcode = src.zipcode
        dest.address_parts = src.address_parts | dest.address_parts

    @staticmethod
    def process_addresses(self):
        _residence = next((x for x in self.address_list if x.address_type == AddressType.RESIDENCE), None)
        _mail = next((x for x in self.address_list if x.address_type == AddressType.MAIL), None)
        if _residence and _mail:
            if _residence.standardized != _mail.standardized:
                score = fuzz.token_sort_ratio(_residence.standardized, _mail.standardized)
                if score > 93:
                    if len(_residence.standardized) > len(_mail.standardized):
                        AddressValidationFuncs.copy_address(_residence, _mail)
                    else:
                        AddressValidationFuncs.copy_address(_mail, _residence)
                elif score > 85 > 93:
                    raise PydanticCustomError(
                        'standardized:address_mismatch',
                        'Residential and Mailing addresses are close to matching, requires manual review.',
                        {
                            'function': 'process_addresses',
                            'addresses': {
                                'residential': _residence.standardized,
                                'mailing': _mail.standardized
                            },
                        }
                    )
            return self


@pydantic_dataclass
class PhoneNumberValidationFuncs:

    @staticmethod
    def check_if_valid_phone(phone_num: str) -> Tuple[phonenumbers.PhoneNumber | None, List[str]]:
        number_corrections = []
        _correct_number = None
        try:
            _correct_number = phonenumbers.parse(phone_num, "US")
        except phonenumbers.phonenumberutil.NumberParseException:
            number_corrections.append('Phone number is not a valid US phone number')
            _correct_number = None
        if _correct_number and not phonenumbers.is_valid_number(_correct_number):
            number_corrections.append('Phone number is not a valid US phone number')
            _correct_number = None
        if not _correct_number:
            number_corrections.append('Phone number is not a valid US phone number')
        return _correct_number, number_corrections

    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[Optional[phonenumbers.PhoneNumber], List[str]]:
        try:
            parsed_number = phonenumbers.parse(phone, "US")
            if phonenumbers.is_valid_number(parsed_number):
                return parsed_number, ["Phone number successfully validated"]
            else:
                return None, ["Phone number is not a valid US phone number"]
        except phonenumbers.NumberParseException:
            return None, ["Failed to parse phone number"]

    @staticmethod
    def format_phone_number(phone: phonenumbers.PhoneNumber) -> Dict[str, str]:
        formatted = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        national_number = str(phone.national_number)
        return {
            "phone": formatted,
            "areacode": national_number[:3],
            "number": national_number[3:]
        }

    @staticmethod
    def validate_phones(self):
        _func = PhoneNumberValidationFuncs
        phone_list = []
        all_corrections = {}
        input_phone_dict = vfuncs.getattr_with_prefix(helpers.CONTACT_PHONE_PREFIX, getattr(self, 'data', None))

        if not input_phone_dict:
            self.phone = None
            return self

        for key, value in input_phone_dict.items():
            if not key.startswith(helpers.CONTACT_PHONE_PREFIX) or not value:
                continue

            phone_type = key.split('_')[2]
            type_prefix = f'{helpers.CONTACT_PHONE_PREFIX}_{phone_type}'

            full_phone = input_phone_dict.get(type_prefix)
            phone_areacode = input_phone_dict.get(f'{type_prefix}_areacode')
            phone_number = input_phone_dict.get(f'{type_prefix}_number')

            corrections = []

            if full_phone:
                parsed_phone, parse_corrections = _func.validate_phone_number(full_phone)
                corrections.extend(parse_corrections)

                if parsed_phone:
                    phone_data = _func.format_phone_number(parsed_phone)
                    phone_data['phone_type'] = phone_type
                    phone_data['reliability'] = input_phone_dict.get(f'{type_prefix}_reliability')
                    phone_list.append(ValidatedPhoneNumber(**phone_data))
                    corrections.append(f'{phone_type} was successfully validated and formatted')

            if phone_areacode and phone_number:
                if len(phone_areacode) == 3 and len(phone_number) == 7:
                    merged_number = f"{phone_areacode}{phone_number}"
                    parsed_merged, merge_corrections = _func.validate_phone_number(merged_number)
                    corrections.extend(merge_corrections)

                    if parsed_merged:
                        formatted_merged = _func.format_phone_number(parsed_merged)
                        formatted_merged['phone_type'] = phone_type
                        formatted_merged['reliability'] = input_phone_dict.get(f'{type_prefix}_reliability')

                        if not any(p.phone == formatted_merged['phone'] for p in phone_list):
                            phone_list.append(ValidatedPhoneNumber(**formatted_merged))
                            corrections.append(f'Additional number added for {phone_type}')

            if corrections:
                all_corrections[phone_type] = corrections

        if phone_list:
            self.corrected_errors.update({f'phone_{k}': v for k, v in all_corrections.items()})
            self.phone = phone_list
        else:
            self.phone = None

        return self


def validate_date_dob(self):
    _date_format = self.date_format

    if not _date_format:
        raise PydanticCustomError(
            'missing_date_format',
            'Date format is missing for voter registration date',
            dict(
                model='PreValidationCleanUp',
                function='validate_dob',
                nested_function='validate_date_dob'
            )
        )
    _dob = None
    valid_dob = None
    dob_corrections = []
    if not self.data.person_dob:
        if self.data.person_dob_yearmonth:
            if self.data.person_dob_day:
                _dob = f"{self.data.person_dob_yearmonth}{self.data.person_dob_day}"
            else:
                _dob = self.data.person_dob = f"{self.data.person_dob_yearmonth}01"
                dob_corrections.append('Combined yearmonth and day values to create a valid date')
        elif self.data.person_dob_year:
            if self.data.person_dob_month and self.data.person_dob_day:
                _dob = f"{self.data.person_dob_year}{self.data.person_dob_month}{self.data.person_dob_day}"
                dob_corrections.append('Combined year, month, and day values to create a valid date')
            elif self.data.person_dob_month:
                _dob = f"{self.data.person_dob_year}{self.data.person_dob_month}01"
                dob_corrections.append('Combined year and month values to create a valid date')
            else:
                _dob = f"{self.data.person_dob_year}0101"
                dob_corrections.append('Combined year and month values to create a valid date')
        else:
            _dob = None

    if self.data.person_dob:
        if isinstance(self.data.person_dob, date):
            valid_dob = self.data.person_dob
        elif isinstance(self.data.person_dob, str):
            _dob = str(self.data.person_dob).replace('-', '')
            if len(_dob) == 6 and '%Y%m%d' in _date_format:
                dob_corrections.append(
                    "DOB only has 6 characters. Attempting to validate by adding 01 for the day.")
                _dob = f"{_dob}01"
        else:
            _dob = None
            dob_corrections.append('DOB is not a valid date. Removed DOB.')

    if _dob:

        if _dob[-2:] == '00':
            _dob = _dob[:-2] + '01'
        if isinstance(_date_format, list):
            for _time_format in _date_format:
                try:
                    valid_dob = datetime.strptime(_dob, _time_format).date()
                except ValueError:
                    continue
                else:
                    break
        elif isinstance(_date_format, str):
            valid_dob = datetime.strptime(_dob, _date_format).date()
        else:
            valid_dob = None
        self.person_details['person_dob'] = valid_dob
        dob_corrections.append('Converted values to a valid date')
        self.corrected_errors.update({'dob': dob_corrections})
    return self


def validate_date_edr(self):
    _date_format = self.date_format
    _voter_registration = self.data.voter_registration_date
    _voter_registration_corrections = []

    if not _voter_registration:
        return self

    if not _date_format:
        raise PydanticCustomError(
            'missing_date_format',
            'Date format is missing for voter registration date',
            dict(
                model='PreValidationCleanUp',
                function='validate_edr',
                nested_function='validate_date_edr'
            )
        )

    # _possible_keys = key_list_with_suffix('registration_date', _voter_registration)
    # if _possible_keys and len(_possible_keys) == 1:
    #     if _date_format:
    if isinstance(_date_format, list):
        for _time_format in _date_format:
            try:
                self.input_voter_registration['edr'] = (
                    datetime.strptime(
                        _voter_registration, _time_format
                    ).date()
                )
            except ValueError:
                continue
            else:
                break
    elif isinstance(_date_format, str):
        try:
            self.input_voter_registration['edr'] = (
                datetime.strptime(
                    _voter_registration, _date_format
                ).date()
            )
            _voter_registration_corrections.append('Converted registration to a valid date')
        except ValueError:
            raise PydanticCustomError(
                'invalid_registration_date',
                'Invalid voter registration date for record: {voter_registration_date}',
                dict(
                    model='PreValidationCleanUp',
                    function='validate_edr',
                    nested_function='validate_date_edr',
                    voter_registration_date=_voter_registration)
            )
        self.corrected_errors.update({'voter_registration': _voter_registration_corrections})
        if not self.input_voter_registration['edr'] and self.data.settings.get('FILE-TYPE') == 'voterfile':
            raise PydanticCustomError(
                'invalid_registration_date',
                'Invalid voter registration date for record: {voter_registration_date}',
                dict(
                    model='PreValidationCleanUp',
                    function='validate_edr',
                    nested_function='validate_date_edr',
                    voter_registration_date=_voter_registration)
            )
    return self


# def validate_phones(self: PreValidationCleanUp) -> PreValidationCleanUp:
#     _formatter = phonenumbers.format_number
#     _input_phone_dict = vfuncs.getattr_with_prefix(helpers.CONTACT_PHONE_PREFIX, self.data)
#     if not _input_phone_dict:
#         return self
#
#     phone_dict = {}
#     _phone_types = [k.split('_')[2] for k, v in _input_phone_dict.items() if
#                     k.startswith(helpers.CONTACT_PHONE_PREFIX) and v]
#     _all_phone_corrections = {}
#
#     for each in _phone_types:
#         _type_pfx = f'{helpers.CONTACT_PHONE_PREFIX}_{each}'
#         _formatted_full_phone = None
#         _formatted_number_parts = None
#         _full_phone = None
#         _number_parts = None
#         _existing_full_phone = _input_phone_dict.get(_type_pfx)
#         _existing_phone_areacode = _input_phone_dict.get(f'{_type_pfx}_areacode')
#         _existing_phone_number = _input_phone_dict.get(f'{_type_pfx}_number')
#         type_corrections = {}
#         type_corrections.setdefault(f'{each}', [])
#         if _existing_full_phone:
#             _full_phone, _full_phone_corrections = check_if_valid_phone(_existing_full_phone)
#             if _full_phone:
#                 _formatted_full_phone = _formatter(_full_phone, phonenumbers.PhoneNumberFormat.E164)
#
#             type_corrections[each].append(_full_phone_corrections)
#
#         if all([_existing_phone_areacode, _existing_phone_number]):
#             if all([len(_existing_phone_areacode) == 3, len(_existing_phone_number) == 7]):
#                 merged_number = f"{_existing_phone_areacode}{_existing_phone_number}"
#                 _number_parts, _number_parts_corrections = check_if_valid_phone(merged_number)
#                 if _number_parts:
#                     _formatted_number_parts = _formatter(_number_parts, phonenumbers.PhoneNumberFormat.E164)
#                 type_corrections[each].append(_number_parts_corrections)
#             else:
#                 raise PydanticCustomError(
#                     f'invalid_{_type_pfx}_format',
#                     f'Invalid {_type_pfx} format.',
#                     dict(
#                         model='PreValidationCleanUp',
#                         function='validate_phones',
#                         nested_function='validate_phones',
#                         areacode=f'{_existing_phone_areacode} ({len(_existing_phone_areacode)})',
#                         number=f'{_existing_phone_number} ({len(_existing_phone_number)})'
#                     )
#                 )
#
#         if _formatted_full_phone and _formatted_number_parts:
#             if _formatted_full_phone != _formatted_number_parts:
#
#                 phone_dict[each] = {
#                     'phone_type': each,
#                     'phone': _formatted_full_phone,
#                     'areacode': str(_full_phone.national_number)[:3],
#                     'number': str(_full_phone.national_number)[3:]
#                 }
#                 type_corrections[each].append(f'{each} was successfully validated and formatted')
#
#                 _type_of_phone = each[:-1]
#                 _type_of_phone_count = int(each[-1:]) + 1
#
#                 mismatch_type = f'{_type_of_phone}{_type_of_phone_count}'
#                 while mismatch_type in _phone_types:
#                     _type_of_phone_count += 1
#                     mismatch_type = f'{_type_of_phone}{_type_of_phone_count}'
#
#                 phone_dict[mismatch_type] = {
#                     'phone_type': mismatch_type,
#                     'phone': _formatted_number_parts,
#                     'areacode': str(_number_parts.national_number)[:3],
#                     'number': str(_number_parts.national_number)[3:]
#                 }
#                 type_corrections[each].append(
#                     f'Full {each} number did not match areacode and number parsed out for the same field. Additional number was set to {mismatch_type}')
#                 type_corrections[each].append(
#                     f'{mismatch_type} was successfully validated and formatted')
#
#             else:
#                 type_corrections[each].append(f'{each} was successfully validated and formatted')
#                 phone_dict[each] = {
#                     'phone_type': each,
#                     'phone': _formatted_full_phone,
#                     'areacode': str(_full_phone.national_number)[:3],
#                     'number': str(_full_phone.national_number)[3:]
#                 }
#
#         elif _formatted_full_phone:
#             type_corrections[each].append(f'{each} was successfully validated and formatted')
#             phone_dict[each] = {
#                 'phone_type': each,
#                 'phone': _formatted_full_phone,
#                 'areacode': str(_full_phone.national_number)[:3],
#                 'number': str(_full_phone.national_number)[3:],
#                 'reliability': _input_phone_dict.get(f'{_type_pfx}_reliability', None)
#             }
#         elif _formatted_number_parts:
#             type_corrections[each].append(f'{each} was successfully validated and formatted')
#             phone_dict[each] = {
#                 'phone_type': each,
#                 'phone': _formatted_number_parts,
#                 'areacode': str(_number_parts.national_number)[:3],
#                 'number': str(_number_parts.national_number)[3:],
#                 'reliability': _input_phone_dict.get(f'{_type_pfx}_reliability', None)
#             }
#         else:
#             _ = None
#
#         if type_corrections:
#             _all_phone_corrections.update(type_corrections)
#
#     if any(phone_dict.values()):
#         self.corrected_errors.update({f'phone_{k}': v for k, v in _all_phone_corrections.items()})
#         ic('Phone Dict', phone_dict)
#         self.phone = list(ValidatedPhoneNumber(**x) for x in phone_dict.values())
#         ic('Validated Phones', self.phone)
#     else:
#         self.phone = None
#     return self


# def validate_vendors(self):
#     new_vendor_dict = None
#     _input_vendor_dict = vfuncs.getattr_with_prefix('vendor', self.data)
#     vendor_corrections = {}
#     if isinstance(_input_vendor_dict, dict):
#         new_vendor_dict = {}
#         vendor_names = [k.split('_')[1] for k, v in _input_vendor_dict.items()]
#         for vendor in vendor_names:
#             vendor_title = f'vendor_{vendor}'
#             vendor_corrections[vendor_title] = ['Parsed vendor name']
#             vendor_dict = vfuncs.dict_with_prefix(pfx=vendor_title, dict_=_input_vendor_dict)
#
#             # Replace vendor title in key via map within vendor dict
#             updated_vendor_dict = {}
#             for k, v in vendor_dict.items():
#                 k_ = k.replace(f'{vendor_title}_', '')
#                 vendor_corrections[vendor_title].append(f'Parsed {k_}')
#                 if k_ == 'id':
#                     k_ = k_ + '_'
#                     vendor_corrections[vendor_title].append(f'Transformed {k_} to be nested under {vendor}')
#                 updated_vendor_dict.update({k_: v})
#             # vendor_dict = {k.replace(f'{vendor_title}_', ''): v for k, v in vendor_dict.items()}
#             new_vendor_dict[vendor] = updated_vendor_dict
#     if new_vendor_dict:
#         self.vendors = new_vendor_dict
#         self.vendor_corrections = vendor_corrections
#     return self


def create_vep_keys(self):
    if not self.name:
        raise PydanticCustomError(
            'missing_name',
            'Missing name details. Unable to generate a strong key to match with',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'create_vep_keys'
            }
        )
    elif not all([first_ := self.name.first, last_ := self.name.last]):
        if not first_:
            missing_name = 'first'
        elif not last_:
            missing_name = 'last'
        else:
            missing_name = 'first and last'

        raise PydanticCustomError(
            f'missing_{missing_name.replace(' ', '_')}_name',
            f'Missing {missing_name} name. Unable to generate a strong key to match with',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'create_vep_keys'
            }
        )

    if not self.name.dob:
        if RAISE_EXCEPTIONS_FOR_CHANGES:
            raise PydanticCustomError(
                'missing_dob',
                'Missing date of birth. Unable to generate a strong key to match with',
                {
                    'validator_model': self.__class__.__name__,
                    'method_type': 'model_validator',
                    'method_name': 'create_vep_keys'
                }
            )
        else:
            _dob = None
    else:
        _dob = str(self.name.dob).replace('-', '')

    if not any([x for x in self.address_list if x.address_type in AddressTypeList]):
        return self

    if addr := next((x for x in self.address_list if x.address_type == AddressType.RESIDENCE), None):
        _zip5, _zip4, _standardized_address = addr.zip5, addr.zip4, addr.standardized
        _uses_mailzip = None
    elif addr := next((x for x in self.address_list if x.address_type == AddressType.MAIL), None):
        _zip5, _zip4, _standardized_address = addr.zip5, addr.zip4, addr.standardized
        _uses_mailzip = True
    else:
        _zip5, _zip4, _standardized_address = None, None, None
        _uses_mailzip = None

    name_ = self.name
    _first_name, _last_name, _dob = name_.first, name_.last, name_.dob

    vep_key_dict = {}

    _initial_name_key = f"{_first_name[:5].strip()}{_last_name[:5].strip()}"
    if _zip5:
        _vep_key = f"{_initial_name_key}{_zip5.strip()}"
        vep_key_dict['short'] = vfuncs.only_text_and_numbers(_vep_key)
        # if _zip4:
        #     _vep_key += f"{_zip4}"
        vep_key_dict['best_key'] = vfuncs.only_text_and_numbers(_vep_key)
        vep_key_dict['full_key'] = vfuncs.only_text_and_numbers(_vep_key)
        vep_key_dict['full_key_hash'] = RecordKeyGenerator(_vep_key).hash
        if _dob:
            _vep_key += f"{_dob}"
            _cleaned_vep_key = vfuncs.only_text_and_numbers(_vep_key)
            vep_key_dict['best_key'] = _cleaned_vep_key
            vep_key_dict['long'] = _cleaned_vep_key
            vep_key_dict['full_key'] = _cleaned_vep_key
            vep_key_dict['full_key_hash'] = RecordKeyGenerator(_cleaned_vep_key).hash

    if _dob:
        _name_key = f"{_initial_name_key}{_dob}"
        _cleaned_name_key = vfuncs.only_text_and_numbers(_name_key)
        vep_key_dict['name_dob'] = _cleaned_name_key
        if not vep_key_dict.get('best_key'):
            vep_key_dict['best_key'] = _cleaned_name_key

    if _standardized_address:
        _address_key = _standardized_address.replace(' ', '').replace(',', '')
        _cleaned_address_key = vfuncs.only_text_and_numbers(_address_key)
        vep_key_dict['addr_text'] = _cleaned_address_key
        vep_key_dict['addr_key'] = RecordKeyGenerator(_cleaned_address_key).hash

    vep_key_dict['uses_mailzip'] = _uses_mailzip

    if any(vep_key_dict.values()):
        if all([x for x in self.address_list if x.address_type in AddressTypeList]):
            _residence = next((x for x in self.address_list if x.address_type == AddressType.RESIDENCE), None)
            if _uses_mailzip and _residence and (_rzip5 := _residence.zip5):
                raise PydanticCustomError(
                    'uses_mailzip_with_residential_zip_present',
                    "VEP Keys are being generated with a Mail Zipcode, But Residential Zips are present",
                    {
                        'mail_zip5': _zip5,
                        'residence_zip5': _rzip5,
                    }
                )
        self.vep_keys = VEPMatch(**{k: v for k, v in vep_key_dict.items() if v})
    else:
        self.vep_keys = None
    return self


def validate_election_history(self) -> Self:
    election_validator = StateElectionHistoryValidator()
    if self.data.settings.get('FILE-TYPE') == 'voterfile':
        if _state_name := self.data.settings.get('STATE').get('abbreviation'):
            match _state_name:
                case 'TX':
                    election_validator.TEXAS(self)
                case _:
                    raise ValueError(f"State not supported: {_state_name}")
    return self


def check_if_fields_exist(self):
    _person_details = self.person_details
    if not _person_details:
        raise PydanticCustomError(
            'missing_person_details',
            'Missing person details. Unable to generate a strong key to match with',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )

    if not self.name and vfuncs.getattr_with_prefix('person_name', self.data):
        raise PydanticCustomError(
            'missing_name_object',
            'There is name data in the renamer, but unable to create a name object',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )
    if not self.phone and (_phone_data := vfuncs.getattr_with_prefix('contact_phone', self.data)):
        if not len(_phone_data) == 1:
            raise PydanticCustomError(
                'missing_phone_object',
                'There is phone data in the renamer, but unable to create a phone object',
                {
                    'validator_model': self.__class__.__name__,
                    'method_type': 'model_validator',
                    'method_name': 'set_validator_types'
                }
            )
    if not any([x for x in self.address_list if x.address_type in AddressTypeList]):
        raise PydanticCustomError(
            'missing_address',
            'Missing address information. Unable to generate VEP keys',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )
    elif self.data.settings.get('FILE-TYPE') == 'VOTERFILE':
        if not self.residential_address:
            raise PydanticCustomError(
                'missing_residential_address',
                'Missing residential address information for voter record.',
                {
                    'validator_model': self.__class__.__name__,
                    'method_type': 'model_validator',
                    'method_name': 'set_validator_types'
                }
            )

    if not self.voter_registration and vfuncs.getattr_with_prefix('voter', self.data):
        raise PydanticCustomError(
            'missing_voter_registration',
            'There is voter registration data in the renamer, but unable to create a voter registration object',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )

    if not self.districts and vfuncs.getattr_with_prefix('district', self.data):
        raise PydanticCustomError(
            'missing_districts',
            'There is district data in the renamer, but unable to create a district object',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )

    if not self.vendors and vfuncs.getattr_with_prefix('vendor', self.data):
        raise PydanticCustomError(
            'missing_vendors',
            'There is vendor data in the renamer, but unable to create a vendor object',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )
    return self


class PreValidationCleanUp(RecordBaseModel):
    data: Annotated[RecordRenamer, Field(...)]
    person_details: Annotated[Optional[Dict[str, Any]], Field(default_factory=dict)]
    input_voter_registration: Annotated[Optional[Dict[str, Any]], Field(default_factory=dict)]
    date_format: Annotated[Any, Field(default=None)]
    settings: Annotated[Optional[Dict[str, Any]], Field(default=None)]
    raw_data: Annotated[Optional[Dict[str, Any]], Field(default=None)]

    def _filter(self, start: str):
        result = vfuncs.getattr_with_prefix(start, obj=self.data)
        assert isinstance(result, dict), f"Expected a dict, got {type(result)}"
        return result

    @model_validator(mode='after')
    def filter_fields(self):
        self.raw_data = _raw_data if (_raw_data := self.data.raw_data) else None
        self.date_format = _date_format if (_date_format := self.data.date_format) else None
        self.settings = _settings if (_settings := self.data.settings) else None
        return self

    @model_validator(mode='after')
    def filter_name(self):
        if not self.name:
            _name = self._filter('person')
            if not _name:
                raise PydanticCustomError(
                    'missing_name',
                    'Missing name details. Unable to generate a strong key to match with',
                    {
                        'validator_model': self.__class__.__name__,
                        'method_type': 'model_validator',
                        'method_name': 'validate_name'
                    }
                )
            _name_dict = vfuncs.remove_prefix(_name, ['person_name_'])
            output_dict = {}
            for k, v in _name_dict.items():
                if k not in list(PersonName.model_fields):
                    output_dict.setdefault('other_fields', {}).update({k: v})
                elif k != 'dob':
                    output_dict[k] = v
                    # TODO: Stopping point before meeting KSB.
            self.person_details.update(output_dict)
        return self

    @model_validator(mode='after')
    def filter_voter_registration(self):
        if not (vr := self._filter('voter')):
            return self

        _reg_details = {k.replace('voter_', ''): v for k, v in vr.items() if v}

        d = {
            'vuid': _reg_details.pop('vuid', None),
            'edr': _reg_details.pop('registration_date', None),
            'status': _reg_details.pop('status', None),
            'county': _reg_details.pop('county', None),
        }
        attributes = {
            'political_tags': {},
        }
        for k, v in _reg_details.items():
            match k:
                case 'profile':
                    attributes['political_tags'].update({k.removeprefix('profile_').strip(): v})
                case _:
                    attributes[k] = v
        if attributes:
            d.update({'attributes': attributes})
        self.input_voter_registration = d
        return self

    @model_validator(mode='after')
    def validate_addresses(self):
        for address_type in AddressTypeList:
            address_count = 0
            while True:
                _func = AddressValidationFuncs
                prefix = f"{address_type}_{address_count}_" if address_count > 0 else f"{address_type}_"
                if not vfuncs.getattr_with_prefix(prefix, self.data):
                    break  # No more addresses of this type

                _address_exists = _func.validate_address(address_type=address_type, _renamed=self.data)
                if not _address_exists:
                    break  # Invalid address, stop processing this type

                _address, _corrections = _address_exists
                d = {}
                self.corrected_errors.setdefault('addresses', {}).update(_corrections)
                _renamed_dict = {k.replace(f'{address_type}_', ''): v for k, v in _address.items() if v}
                other_fields = {}
                for k, v in _renamed_dict.items():
                    if k not in list((addr := Address).model_fields):
                        other_fields[k] = v
                    else:
                        d[k] = v
                if other_fields:
                    d.setdefault('other_fields', {}).update(other_fields)
                d['address_type'] = address_type
                self.address_list.append(Address(**d))
                address_count += 1  # Increment to check for additional addresses

        return self

    validate_edr = model_validator(mode='after')(validate_date_edr)
    validate_phones = model_validator(mode='after')(PhoneNumberValidationFuncs.validate_phones)
    validate_dob = model_validator(mode='after')(validate_date_dob)
    validate_elections = model_validator(mode='after')(validate_election_history)

    @model_validator(mode='after')
    def validate_name(self):
        if self.person_details:
            self.person_details = vfuncs.remove_prefix(self.person_details, ['person_', ])
            self.name = PersonName(**self.person_details)
        return self

    # validate_vendors = model_validator(mode='after')(validate_vendors)

    @model_validator(mode='after')
    def validate_voter_registration(self):
        if self.input_voter_registration:
            self.voter_registration = VoterRegistration(**self.input_voter_registration)
        return self

    @model_validator(mode='after')
    def validate_vendors(self):
        new_vendor_dict = None
        _input_vendor_dict = vfuncs.getattr_with_prefix('vendor', self.data)
        if not isinstance(_input_vendor_dict, dict):
            return self

        new_vendor_dict = {}
        vendor_names = set(k.split('_')[1] for k in _input_vendor_dict.keys())
        vendors_to_return = []
        for vendor in vendor_names:
            vendor_title = f'vendor_{vendor}'
            vendor_dict = vfuncs.dict_with_prefix(pfx=vendor_title, dict_=_input_vendor_dict)
            new_vendor_dict[vendor] = {k.replace(f'{vendor_title}_', ''): v for k, v in vendor_dict.items() if v}
        if new_vendor_dict:
            for k, v in new_vendor_dict.items():
                if v:
                    for _k, _v in v.items():
                        try:
                            _v = str(int(float(_v)))
                        except:
                            pass
                        v[_k] = _v
                    vendors_to_return.append(VendorTags(vendor=k, tags=v))

            self.vendors = vendors_to_return
        return self

    def validate_districts(self):
        _settings = self.settings
        if not _settings:
            return self

        _remove: Dict[str, Dict[str, List[str, str]]] = _settings.get('REMOVE-CHARS')

        if self.districts and _remove:
            _district_corrections = {}
            for _field, _field_replace_list in _remove.items():
                _text_to_remove, _field_to_remove_from = _field_replace_list
                for d in self.districts:
                    if _field_to_remove_from in d.name:
                        d.name = d.name.upper().replace(_text_to_remove, "")
                        _district_corrections[d.type] = [
                            f"Removed '{_text_to_remove}' from '{d.name}'"
                        ]
                # _value = self.districts.get(_field_to_remove_from)
                # if _value:
                #     self.districts[_field_to_remove_from] = _value.upper().replace(_text_to_remove, "")
                #     _district_corrections[_field_to_remove_from] = [
                #         f"Removed '{_text_to_remove}' from '{_value}'"
                #     ]
            if _district_corrections:
                self.corrected_errors.update({'districts': _district_corrections})
        return self

    #
    @model_validator(mode='after')
    def set_districts(self):

        def _filter(district: str):
            data = {
                k.replace(f'district_{district}_', ''): v
                for k, v in _districts.items() if k.startswith(f'district_{district}') and v
            }
            if not data:
                return None

            d = {'type': district}
            for k, v in data.items():
                if any(substring in k for substring in ['upper', 'lower', 'congressional']):
                    d['number'] = v
                    d['name'] = ' '.join(k.split('_'))
                elif 'name' in k:
                    d['name'] = v
                else:
                    d.setdefault('attributes', {}).update({k: v})
            return District(**d)

        _districts = vfuncs.getattr_with_prefix('district', self.data)
        if _districts:
            districts = {
                'city': _filter('city'),
                'county': _filter('county'),
                'state': _filter('state'),
                'federal': _filter('federal'),
                'court': _filter('court'),
            }
            if not any(list(districts.values())):
                self.districts = None
            else:
                self.districts = list(v for k, v in districts.items() if v)
                self.corrected_errors.update(
                    {f'{k}_districts': 'Parsed district information' for k, v in districts.items() if v}
                )
        return self

    check_for_fields = model_validator(mode='after')(check_if_fields_exist)

    @model_validator(mode='after')
    def set_validator_types(self):
        AddressValidationFuncs.process_addresses(self)
        self.name = PersonName(**vfuncs.remove_prefix(self.person_details, ['person_name_', 'person_']))
        _input_data = {
            'original_data': self.raw_data,
            'renamed_data': dict(self.data),
            'corrections': self.corrected_errors,
            'settings': self.settings,
            'date_format': self.date_format

        }
        [_input_data['renamed_data'].pop(x, None) for x in ['raw_data', 'settings', 'date_format']]
        # _input_data['renamed_data'].pop('raw_data', None)
        # _input_data['renamed_data'].pop('settings', None)
        # _input_data['renamed_data'].pop('date_format', None)
        self.input_data = InputData(**_input_data)
        return self

    generate_vep_keys = model_validator(mode='after')(create_vep_keys)
