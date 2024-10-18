
from typing import Any, Dict, List
from functools import partial
from enum import StrEnum

import usaddress
from rapidfuzz import fuzz

from pydantic_core import PydanticCustomError
from pydantic.dataclasses import dataclass as pydantic_dataclass

import state_voterfiles.utils.validation.default_helpers as helpers
import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
from state_voterfiles.utils.pydantic_models.rename_model import RecordRenamer


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
