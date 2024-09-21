from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional, Annotated, Self, Set, Iterable, Type, Generator, Union
from datetime import datetime, date
from functools import partial
from enum import StrEnum
import uuid
from collections import defaultdict

import usaddress
import phonenumbers
# import logfire
from icecream import ic
from rapidfuzz import fuzz

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError
from pydantic import ValidationError, BaseModel, Field
from pydantic.dataclasses import dataclass as pydantic_dataclass

from state_voterfiles.utils.pydantic_models.rename_model import RecordRenamer
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
import state_voterfiles.utils.validation.default_helpers as helpers
import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.validation.texas_elections import TexasElectionHistoryValidator
from state_voterfiles.utils.pydantic_models.field_models import (
    ValidatorConfig,
    ValidatedPhoneNumber,
    Address,
    PersonName,
    VoterRegistration,
    VEPMatch,
    District,
    RecordDistrict,
    CustomFields,
    VendorName,
    VendorTags,
    InputData,
    RecordBaseModel,
    DataSource
)
from state_voterfiles.utils.pydantic_models.election_details import (
    VotedInElection,
    ElectionTypeDetails,
    ElectionList
)
from state_voterfiles.utils.helpers.district_codes import DistrictCodes
from state_voterfiles.utils.funcs.validation.address import AddressType, AddressValidationFuncs, AddressTypeList
from state_voterfiles.utils.funcs.validation.phone import PhoneNumberValidationFuncs
from state_voterfiles.utils.funcs.validation.vep_keys import VEPKeyMaker
from state_voterfiles.utils.funcs.validation.dates import DateValidators
from state_voterfiles.utils.funcs.validation.election_history import ElectionValidationFuncs
ic.enable()
ic.configureOutput(prefix='PreValidationCleanUp| ', includeContext=True)

# TODO: Check districts to make sure they validate TODO: Remove all validation aliases so that we can use SQLModel
#  directly for the models
# TODO: Run validation on state voterfiles, specifically Texas to ensure changes made to
#   validation process in cleanup still work.

RAISE_EXCEPTIONS_FOR_CHANGES = False

# Define type aliases for readability
PassedRecords = Iterable[Type[ValidatorConfig]]
InvalidRecords = Iterable[Type[ValidatorConfig]]
ValidationResults = Tuple[PassedRecords, InvalidRecords]


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


# TODO: Modify to create a collected phones set

# TODO: Modify Address Storage so it keeps address ID from address collections table in the record information

# TODO: Figure out a way to do district combinations so there's a table of combinations linked to each other
#  and that combination table can be linked to the record.

# TODO: With the district combinations, figure out a way to check if there's some districts, but not others already
#  in the database, if so, go ahead and expand the comination into the record.
#  May not need to do that though if it's just generating a list of districts and creating combinations accordingly.
class PreValidationCleanUp(RecordBaseModel):
    data: Annotated[RecordRenamer, Field(...)]
    person_details: Annotated[Optional[Dict[str, Any]], Field(default_factory=dict)]
    input_voter_registration: Annotated[Optional[Dict[str, Any]], Field(default_factory=dict)]
    date_format: Annotated[Any, Field(default=None)]
    settings: Annotated[Optional[Dict[str, Any]], Field(default=None)]
    raw_data: Annotated[Optional[Dict[str, Any]], Field(default=None)]
    collected_vendors: Annotated[Set[VendorName], Field(default_factory=set)]
    collected_addresses: Annotated[Set[Address], Field(default_factory=set)]
    collected_elections: Annotated[Set[ElectionTypeDetails], Field(default_factory=set)]
    collected_districts: Annotated[Set[District], Field(default_factory=set)]
    collected_phones: Annotated[Set[ValidatedPhoneNumber], Field(default_factory=set)]

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

    validate_edr = model_validator(mode='after')(DateValidators.validate_date_edr)
    validate_phones = model_validator(mode='after')(PhoneNumberValidationFuncs.validate_phones)
    validate_dob = model_validator(mode='after')(DateValidators.validate_date_dob)
    validate_elections = model_validator(mode='after')(ElectionValidationFuncs.validate_election_history)

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
                vendor_obj = VendorName(name=k)
                self.collected_vendors.add(vendor_obj)
                if v:
                    for _k, _v in v.items():
                        try:
                            _v = str(int(float(_v)))
                        except:
                            pass
                        v[_k] = _v
                    vendors_to_return.append(VendorTags(vendor_id=vendor_obj.id, tags=v))

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

    @model_validator(mode='after')
    def set_districts(self):
        def _filter(district: str, district_codes_enum):
            data = {
                k.replace(f'district_{district}_', ''): v
                for k, v in _districts.items() if k.startswith(f'district_{district}') and v
            }
            if not data:
                return None

            sorted_data = dict(sorted(data.items(), key=lambda item: len(item[0]), reverse=True))

            level_districts = []
            for k, v in sorted_data.copy().items():
                d = {'type': district, 'number': None, 'name': None, 'district_code': None}
                _attributes = {'last_updated': f"{datetime.now(): %Y-%m-%d}"}
                # Match the key to the correct enum value
                if district_codes_enum:
                    for enum_member in district_codes_enum:

                        if (_enum := enum_member.name.lower()) in k:
                            em = _enum.replace('_', ' ')
                            k_ = k.replace('_', ' ')
                            if fuzz.token_sort_ratio(em, k_) > 90:
                                d['name'] = enum_member.value  # Assign the enum value
                            else:
                                d['name'] = k
                                break  # Stop once a match is found
                            # Extract letters (district code) and numbers (district number)
                            district_code = ''.join(filter(str.isalpha, v))  # Keep the letters
                            district_number = ''.join(filter(str.isdigit, v))  # Keep the numbers
                            d['number'] = district_number
                            _attributes.update({'district_code_prefix': district_code})

                # # Check if the key is a 'name' field
                # if 'name' in k:
                #     d['name'] = v
                # else:
                #     _attributes.update({k.replace('_', ' ' ): v.replace('_', ' ')})

                additional_attributes = {}
                if _has_city := self.data.settings.get('CITY'):
                    if _city := _has_city.get('name'):
                        d['city'] = _city
                elif _has_county := self.data.settings.get('COUNTY'):
                    if _county := _has_county.get('name'):
                        d['county'] = _county
                elif _has_state := self.data.settings.get('STATE'):
                    if _state := _has_state.get('abbreviation'):
                        d['state_abbv'] = _state
                if additional_attributes:
                    _attributes.update(additional_attributes)
                d['state_abbv'] = self.data.settings.get('STATE').get('abbreviation')
                d['attributes'] = _attributes
                level_districts.append(District(**d))
            return level_districts

        _districts = vfuncs.getattr_with_prefix('district', self.data)

        if _districts:
            # Map enums for each level
            districts = {
                'city': _filter('city', DistrictCodes.POLITICAL.CITY),
                'county': _filter('county', DistrictCodes.POLITICAL.COUNTY),
                'state': _filter('state', DistrictCodes.POLITICAL.STATE),
                'federal': _filter('federal', DistrictCodes.POLITICAL.FEDERAL),
                'court': _filter('court', DistrictCodes.COURT)
            }
            if not any(list(districts.values())):
                self.districts = None
            else:
                _districts = [district for sublist in districts.values() if sublist for district in sublist]
                _district_ids = [RecordDistrict(district_id=x.id) for x in _districts]
                for sublist in districts.values():
                    if sublist:
                        for district in sublist:
                            self.collected_districts.add(district)
                self.collected_districts.update(
                    {
                        district for sublist in districts.values() if sublist for district in sublist
                    }
                )
                self.districts = _district_ids
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

    generate_vep_keys = model_validator(mode='after')(VEPKeyMaker.create_vep_keys)

    @model_validator(mode='after')
    def set_file_origin(self):
        _file_list = [f for f, _ in self.data_sources]
        if (_file_origin := self.input_data.original_data.get('file_origin')) not in _file_list:
            self.data_sources.append(DataSource(file=_file_origin))
        return self
