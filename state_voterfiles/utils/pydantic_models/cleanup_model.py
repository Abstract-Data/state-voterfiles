from typing import Any, Dict, List, Tuple, Optional, Annotated, Set, Iterable, Type
from datetime import datetime
from enum import StrEnum

# import logfire
from icecream import ic
from rapidfuzz import fuzz

from pydantic import model_validator
from pydantic_core import PydanticCustomError

import state_voterfiles.utils.validation.default_funcs as vfuncs
# from ..db_models.record import RecordBaseModel
# from ..pydantic_models.rename_model import RecordRenamer
from state_voterfiles.utils.pydantic_models.config import ValidatorConfig
from state_voterfiles.utils.db_models.validator_record import *
from state_voterfiles.utils.db_models.fields.district import District
# from ..db_models.fields.address import AddressLink
# from ..db_models.fields.vendor import VendorTagsToVendorLink, VendorTagsToVendorToRecordLink
# from ..db_models.fields.phone_number import ValidatedPhoneNumber, PhoneLink
from ..db_models.fields.elections import ElectionVote
# from ..db_models.fields.vep_keys import VEPMatch
# from ..db_models.fields.data_source import DataSourceLink
# from ..db_models.fields.district import DistrictLink, DistrictLinkToRecord
# from ..db_models.categories.district_list import FileDistrictList
from state_voterfiles.utils.helpers.district_codes import DistrictCodes
from state_voterfiles.utils.funcs.validation.address import (
    AddressValidationFuncs,
    AddressTypeList,
    AddressType
)
from state_voterfiles.utils.funcs.validation.phone import PhoneNumberValidationFuncs
from state_voterfiles.utils.funcs.validation.vep_keys import VEPKeyMaker
from state_voterfiles.utils.funcs.validation.dates import DateValidators
from state_voterfiles.utils.funcs.validation.election_history import ElectionValidationFuncs
# from ..db_models.record import RecordBaseModel
# from state_voterfiles.utils.funcs.validation.phone import PhoneNumberValidationFuncs
# from state_voterfiles.utils.funcs.validation.vep_keys import VEPKeyMaker
# from state_voterfiles.utils.funcs.validation.dates import DateValidators
# from state_voterfiles.utils.funcs.validation.election_history import ElectionValidationFuncs
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
    if not any([x.address_type for x in self.address_list if x.address_type in AddressTypeList]):
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

    if not self.district_set.districts and vfuncs.getattr_with_prefix('district', self.data):
        raise PydanticCustomError(
            'missing_districts',
            'There is district data in the renamer, but unable to create a district object',
            {
                'validator_model': self.__class__.__name__,
                'method_type': 'model_validator',
                'method_name': 'set_validator_types'
            }
        )

    if not self.vendor_names and vfuncs.getattr_with_prefix('vendor_names', self.data):
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
class PreValidationCleanUp(CleanUpBaseModel):
    name_id: Optional[int] = SQLModelField(default=None)

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
                if k == 'person_gender':
                    output_dict['gender'] = v
                elif k != 'dob' or k != 'person_dob':
                    output_dict[k] = v
                    # TODO: Stopping point before meeting KSB.
                elif k not in list(PersonName.model_fields):
                    output_dict.setdefault('other_fields', {}).update({k: v})
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
            'status': next((_reg_details[item] for item in _reg_details if item.endswith('status')), None),
            'precinct_number': next((_reg_details[item] for item in _reg_details if item.endswith('precinct_number')), None),
            'precinct_name': next((_reg_details[item] for item in _reg_details if item.endswith('precinct_name')), None),
            'county': _reg_details.pop('county', None),
        }
        attributes = {
            'political_tags': {},
        }
        for k, v in _reg_details.items():
            match k:
                case 'profile':
                    attributes['political_tags'].update({k.removeprefix('profile_').strip(): v})
                case _ if k not in d:
                    attributes[k] = v
        if attributes:
            d.update({'attributes': attributes})
        self.input_voter_registration = d
        return self

    @model_validator(mode='after')
    def validate_addresses(self):
        address_list: Set[Address] = set()
        address_count: Dict[AddressType, int] = {AddressType.RESIDENCE: 0, AddressType.MAIL: 0}

        for address_type in AddressType:
            count = 0
            while True:
                prefix = f"{address_type.value}_{count}_" if count > 0 else f"{address_type.value}_"  # type: ignore
                if not vfuncs.getattr_with_prefix(prefix, self.data):
                    break

                address_data = AddressValidationFuncs.validate_address(
                    address_type=address_type.value,
                    _renamed=self.data)  # type: ignore[assignment]
                if not address_data:
                    break

                address, corrections = address_data
                self.corrected_errors.setdefault('addresses', {}).update(corrections)

                renamed_dict = {
                    k.replace(f'{address_type.value}_', ''): v for k, v in address.items() if v}  # type: ignore
                other_fields = {k: v for k, v in renamed_dict.items() if k not in Address.model_fields}
                address_fields = {k: v for k, v in renamed_dict.items() if k in Address.model_fields}

                address_fields['address_type'] = address_type.value  # type: ignore
                address_fields['other_fields'] = other_fields
                address_fields['is_mailing'] = address_type == AddressType.MAIL
                address_fields['is_residence'] = address_type == AddressType.RESIDENCE

                new_address = Address(**address_fields)
                address_list.add(new_address)
                address_count[address_type] += 1  # type: ignore
                count += 1

        total_addresses = sum(address_count.values())

        if total_addresses == 2 and len(address_list) == 1:
            single_address = address_list.pop()
            single_address.is_residence = True
            single_address.is_mailing = True
            address_list.add(single_address)
        elif total_addresses == 2 and len(address_list) == 2:
            for address in address_list:
                address.is_mailing = address.address_type == AddressType.MAIL.value
                address.is_residence = address.address_type == AddressType.RESIDENCE.value
        elif len(address_list) == 1:
            single_address = next(iter(address_list))
            single_address.is_residence = single_address.address_type == AddressType.RESIDENCE.value
            single_address.is_mailing = single_address.address_type == AddressType.MAIL.value

        self.address_list = address_list
        return self

    # @model_validator(mode='after')
    # def validate_addresses(self):
    #     _address_list = set()
    #     address_count = 0
    #     for address_type in AddressTypeList:
    #         while True:
    #             _func = AddressValidationFuncs
    #             prefix = f"{address_type}_{address_count}_" if address_count > 0 else f"{address_type}_"
    #             if not vfuncs.getattr_with_prefix(prefix, self.data):
    #                 break  # No more addresses of this type
    #
    #             _address_exists = _func.validate_address(address_type=address_type, _renamed=self.data)
    #             if not _address_exists:
    #                 break  # Invalid address, stop processing this type
    #
    #             _address, _corrections = _address_exists
    #             d = {}
    #             self.corrected_errors.setdefault('addresses', {}).update(_corrections)
    #             _renamed_dict = {k.replace(f'{address_type}_', ''): v for k, v in _address.items() if v}
    #             other_fields = {}
    #             for k, v in _renamed_dict.items():
    #                 if k not in list((addr := Address).model_fields):
    #                     other_fields[k] = v
    #                 else:
    #                     d[k] = v
    #             if other_fields:
    #                 d.setdefault('other_fields', {}).update(other_fields)
    #             d['address_type'] = address_type
    #             _address = Address(**d)
    #             if address_type == 'mail':
    #                 _address.is_mailing = True
    #             elif address_type == 'residential':
    #                 _address.is_residence = True
    #             _address_list.add(_address)
    #             address_count += 1  # Increment to check for additional addresses
    #     if address_count == 2 and len(_address_list) == 1:
    #         _single_address = _address_list.pop()
    #         _single_address.is_residence = True
    #         _single_address.is_mailing = True
    #         _address_list.add(_single_address)
    #     elif address_count == 2 and len(_address_list) == 2:
    #         _mailing_address = next((x for x in _address_list if x.is_mailing), None)
    #         _mailing_address.is_mailing = True
    #         _residence_address = next((x for x in _address_list if x.is_residence), None)
    #         _residence_address.is_residence = True
    #     else:
    #         _single_address = next(iter(_address_list), None)
    #         if _single_address:
    #             _single_address.is_residence = True if _single_address.address_type == AddressType.RESIDENCE else None
    #             _single_address.is_mailing = True if _single_address.address_type == AddressType.MAIL else None
    #     self.address_list = _address_list
    #     return self

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

    @model_validator(mode='after')
    def validate_voter_registration(self):
        if self.input_voter_registration:
            status = None
            status_key = next((k for k in self.input_voter_registration.keys() if k.endswith('status')), None)
            # precinct_number_key = next((k for k in self.input_voter_registration.keys() if k.endswith('precinct_number')), None)
            # precinct_name_key = next((k for k in self.input_voter_registration.keys() if k.endswith('precinct_name')), None)
            if status_key:
                status = self.input_voter_registration.pop(status_key)
            # if precinct_number_key:
            #     precinct_number = self.input_voter_registration.pop(precinct_number_key)
            # if precinct_name_key:
            #     precinct_name = self.input_voter_registration.pop(precinct_name_key)
            self.voter_registration = VoterRegistration(
                **self.input_voter_registration,
                status=status,
            )
        return self

    @model_validator(mode='after')
    def validate_vendors(self):
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
                self.vendor_names.add(vendor_obj)
                if v:
                    for _k, _v in v.items():
                        try:
                            _v = str(int(float(_v)))
                        except:
                            pass
                        v[_k] = _v
                    vendors_to_return.append(VendorTags(tags=v))
            self.vendor_tags = vendors_to_return
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
                            if district_code:
                                _attributes['district_code_prefix'] = district_code

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
            # else:
            all_districts = [district for sublist in districts.values() if sublist for district in sublist]

            if all_districts:
                for district in all_districts:
                    self.district_set.add_or_update(district)
                self.corrected_errors.update(
                    {f'{k}_districts': 'Parsed district information' for k, v in districts.items() if v}
                )
        return self

    check_for_fields = model_validator(mode='after')(check_if_fields_exist)

    @model_validator(mode='after')
    def set_vuid_in_vote_history(self):
        if self.elections:
            for election in self.elections:
                election.vote_record.voter_id = self.voter_registration.vuid
                # v.id = v.generate_hash_key()
        return self

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
        self.input_data = InputData(**_input_data)
        return self

    generate_vep_keys = model_validator(mode='after')(VEPKeyMaker.create_vep_keys)

    @model_validator(mode='after')
    def set_file_origin(self):
        if _file_origin := self.input_data.original_data.get('file_origin'):
            self.data_source.append(DataSource(file=_file_origin))
        return self

    # @staticmethod
    # def create_relationships_on_cleanup(record_model: Type[SQLModel]):
    #
    #     AddressLink.address_id = SQLModelField(
    #         default=None,
    #         foreign_key=f"{Address.__tablename__}.id",
    #         primary_key=True)
    #     AddressLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'f{record_model.__tablename__}.id',
    #         primary_key=True)
    #     Address.records = Relationship(
    #         back_populates='address_list',
    #         link_model=AddressLink)
    #
    #     PhoneLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'{record_model.__tablename__}.id',
    #         primary_key=True)
    #
    #     ValidatedPhoneNumber.records = Relationship(
    #         back_populates='phone',
    #         link_model=PhoneLink)
    #
    #     VendorTags.vendors = Relationship(back_populates="tags", link_model=VendorTagsToVendorLink)
    #     VendorName.tags = Relationship(back_populates="vendors", link_model=VendorTagsToVendorLink)
    #
    #     VendorTagsToVendorToRecordLink.record_id = SQLModelField(default=None, foreign_key="record_base.id", primary_key=True)
    #     VendorTagsToVendorToRecordLink.record = Relationship(back_populates='vendor_tag_record_links')
    #
    #     # # Relationships from elections.py
    #     ElectionLinkToRecord.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'{record_model.__tablename__}.id',
    #         primary_key=True)
    #     ElectionLinkToRecord.record = Relationship(back_populates="election_link_records")
    #
    #     # Relationships from data_source.py
    #     DataSource.records = Relationship(
    #         back_populates='data_source',
    #         link_model=DataSourceLink)
    #
    #     DataSourceLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f'{record_model.__tablename__}.id',
    #         primary_key=True)
    #
    #     # Relationships from district.py
    #     DistrictLink.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f"{record_model.__tablename__}.id",
    #         primary_key=True)
    #     DistrictLinkToRecord.record_id = SQLModelField(
    #         default=None,
    #         foreign_key=f"{record_model.__tablename__}.id",
    #         primary_key=True)
    #     DistrictLinkToRecord.record = Relationship(back_populates="district_link_records")
    #     configure_mappers()
    #     return record_model

    # @model_validator(mode='after')
    # def set_foreign_ids(self):
    #     if self.data_source:
    #         self.data_source_id = self.data_source.id
    #     if self.input_data:
    #         self.input_data_id = self.input_data.id
    #     if self.name:
    #         self.name_id = self.name.id
    #     if self.voter_registration:
    #         self.voter_registration_id = self.voter_registration.id
    #     if self.district_set:
    #         self.district_set_id = self.district_set.id
    #     return self