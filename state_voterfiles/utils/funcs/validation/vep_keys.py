from __future__ import annotations

from pydantic_core import PydanticCustomError
from pydantic.dataclasses import dataclass as pydantic_dataclass

import state_voterfiles.utils.validation.default_funcs as vfuncs
from state_voterfiles.utils.funcs.validation.address import AddressType, AddressTypeList
from state_voterfiles.utils.funcs.record_keygen import RecordKeyGenerator
from state_voterfiles.utils.db_models.fields.vep_keys import VEPMatch


@pydantic_dataclass
class VEPKeyMaker:

    @staticmethod
    def create_vep_keys(self, exceptions: bool = False):
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
            if exceptions:
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
