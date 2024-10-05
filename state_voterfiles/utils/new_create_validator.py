from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import field, dataclass
from typing import Tuple, Iterable, Dict, Any, Optional, Generator, Set

from state_voterfiles.utils.abcs.create_validator_abc import (
    CreateValidatorABC,
    ValidatorConfig,
    RunValidationOutput,
    ErrorDetails
)
from .pydantic_models.rename_model import RecordRenamer
from .pydantic_models.cleanup_model import PreValidationCleanUp, RecordBaseModel
from .db_models.categories.election_list import FileElectionList
from .db_models.categories.address_list import FileAddressList
from .db_models.categories.vendor_list import FileVendorNameList
from .db_models.categories.district_list import FileDistrictList
from .db_models.categories.phone_numbers_list import FilePhoneNumberList


class RecordRenameValidator(CreateValidatorABC):
    validator: RecordRenamer


class CleanUpRecordValidator(CreateValidatorABC):
    validator: PreValidationCleanUp = field(default=PreValidationCleanUp)


class FinalValidation(CreateValidatorABC):
    validator: RecordBaseModel


# @dataclass
# class CreateValidator:
#     state_name: Tuple[str, str]
#     renaming_validator: RecordRenamer | RecordRenameValidator
#     record_validator: RecordBaseModel | FinalValidation
#     cleanup_validator: CleanUpRecordValidator | PreValidationCleanUp = field(default=PreValidationCleanUp)
#     _records: Optional[Iterable[Dict[str, Any]]] = field(default=None, init=False)
#     _validation_pipeline: Optional[Generator[RunValidationOutput]] = field(default=None, init=False)
#
#     def __post_init__(self):
#         self.renaming_validator = RecordRenameValidator(self.state_name, self.renaming_validator)
#         self.record_validator = FinalValidation(self.state_name, self.record_validator)
#         self.cleanup_validator = CleanUpRecordValidator(self.state_name, self.cleanup_validator)
#
#     @property
#     def valid(self) -> Generator[ValidatorConfig, None, None]:
#         if self._validation_pipeline is None:
#             raise ValueError("run_validation must be called before accessing valid records")
#         for status, record in self._validation_pipeline:
#             if status == 'valid':
#                 yield record
#             if status == 'invalid':
#                 self.renaming_validator._invalid_count += 1
#
#     @property
#     def invalid(self) -> Generator[Dict[str, Any], None, None]:
#         if self._validation_pipeline is None:
#             raise ValueError("run_validation must be called before accessing invalid records")
#         for status, record in self._validation_pipeline:
#             if status == 'invalid':
#                 yield record
#             if status == 'valid':
#                 self.renaming_validator._valid_count += 1
#
#     def validate_single_record(self, record: Dict[str, Any]) -> Tuple[str, Any]:
#         renamed_record_gen = self.renaming_validator.validate_single_record(record)
#         renamed_result = next(renamed_record_gen)
#         if renamed_result[0] == 'valid':
#             renamed_dict = dict(renamed_result[1])
#             renamed_dict['data'] = renamed_result[1]
#             cleaned_record_gen = self.cleanup_validator.validate_single_record(renamed_dict)
#             cleaned_result = next(cleaned_record_gen)
#             if cleaned_result[0] == 'valid':
#                 final_record_gen = self.record_validator.validate_single_record(dict(cleaned_result[1]))
#                 final_result = next(final_record_gen)
#                 return final_result
#             else:
#                 return 'invalid', ErrorDetails(
#                     model=self.cleanup_validator.__class__.__name__,
#                     point_of_failure="cleanup",
#                     errors=cleaned_result[1].errors
#                 )
#         else:
#             return 'invalid', ErrorDetails(
#                 model=self.renaming_validator.__class__.__name__,
#                 point_of_failure="rename",
#                 errors=renamed_result[1].errors
#             )
#
#     def create_validation_pipeline(self) -> Generator[RunValidationOutput]:
#         if self._records is None:
#             raise ValueError("run_validation must be called before creating the validation pipeline")
#
#         with ThreadPoolExecutor() as executor:
#             futures = (executor.submit(self.validate_single_record, record) for record in self._records)
#             for future in as_completed(futures):
#                 yield future.result()
#
#     def run_validation(self, records: Iterable[Dict[str, Any]]) -> None:
#         self._records = records
#         self._validation_pipeline = self.create_validation_pipeline()
#
#     def get_error_summary(self) -> Dict[str, int]:
#         error_summary = {}
#         for validator in [self.renaming_validator, self.cleanup_validator, self.record_validator]:
#             for error in validator.invalid:
#                 error_type = error['error_type']
#                 error_summary[error_type] = error_summary.get(error_type, 0) + 1
#         return error_summary


@dataclass
class CreateValidator:
    state_name: Tuple[str, str]
    renaming_validator: RecordRenamer | RecordRenameValidator
    record_validator: RecordBaseModel | FinalValidation
    cleanup_validator: CleanUpRecordValidator | PreValidationCleanUp = field(default=PreValidationCleanUp)
    elections: FileElectionList = field(default_factory=FileElectionList)
    vote_type_set: Set[str] = field(default_factory=set)
    addresses: FileAddressList = field(default_factory=FileAddressList)
    vendors: FileVendorNameList = field(default_factory=FileVendorNameList)
    districts: FileDistrictList = field(default_factory=FileDistrictList)
    phone_numbers: FilePhoneNumberList = field(default_factory=FilePhoneNumberList)
    _records: Optional[Iterable[Dict[str, Any]]] = field(default=None, init=False)
    _validation_pipeline: Optional[Generator[RunValidationOutput, None, None]] = field(default=None, init=False)

    def __post_init__(self):
        self.renaming_validator = RecordRenameValidator(self.state_name, self.renaming_validator)
        self.record_validator = FinalValidation(self.state_name, self.record_validator)
        self.cleanup_validator = CleanUpRecordValidator(self.state_name, self.cleanup_validator)

    @property
    def valid(self) -> Generator[ValidatorConfig, None, None]:
        if self._validation_pipeline:
            # raise ValueError("run_validation must be called before accessing valid records")
            for status, record in self._validation_pipeline:
                if status == 'valid':
                    # self._handle_collected_groups(record)
                    yield record
                if status == 'invalid':
                    self.renaming_validator._invalid_count += 1

    @property
    def invalid(self) -> Generator[Dict[str, Any], None, None]:
        if self._validation_pipeline:
            # raise ValueError("run_validation must be called before accessing invalid records")
            for status, record in self._validation_pipeline:
                if status == 'invalid':
                    # self._handle_collected_groups(record)
                    yield record
                if status == 'valid':
                    self.renaming_validator._valid_count += 1

    def _handle_collected_groups(self, cleaned_record: RecordBaseModel) -> None:
        if _elections := cleaned_record.vote_history:
            for e in _elections:
                self.elections.add_or_update(e.election)
                self.vote_type_set.add(e.id)

        if _addresses := cleaned_record.address_list:
            for a in _addresses:
                self.addresses.add_or_update(a)

        if _vendors := cleaned_record.vendor_names:
            for v in _vendors:
                self.vendors.add_or_update(v)

        if _districts := cleaned_record.district_set.districts:
            for d in _districts:
                self.districts.add_or_update(d)

        if _phone_numbers := cleaned_record.phone:
            for p in _phone_numbers:
                self.phone_numbers.add_or_update(p)

    def validate_single_record(self, record: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
        renamed_record_gen = self.renaming_validator.validate_single_record(record)
        renamed_result = next(renamed_record_gen)
        if renamed_result[0] == 'valid':
            renamed_dict = dict(renamed_result[1])
            renamed_dict['data'] = renamed_result[1]
            cleaned_record_gen = self.cleanup_validator.validate_single_record(renamed_dict)
            cleaned_result = next(cleaned_record_gen)
            if cleaned_result[0] == 'valid':
                # self._handle_collected_groups(cleaned_result)
                final_record_gen = self.record_validator.validate_single_record(dict(cleaned_result[1]))
                final_result = next(final_record_gen)
                yield final_result
            else:
                yield 'invalid', ErrorDetails(
                    model=self.cleanup_validator.__class__.__name__,
                    point_of_failure="cleanup",
                    errors=cleaned_result[1].errors
                )
        else:
            yield 'invalid', ErrorDetails(
                model=self.renaming_validator.__class__.__name__,
                point_of_failure="rename",
                errors=renamed_result[1].errors
            )

    def create_validation_pipeline(self) -> Generator[RunValidationOutput]:
        if self._records is None:
            raise ValueError("run_validation must be called before creating the validation pipeline")

        for record in self._records:
            yield from self.validate_single_record(record)

    def run_validation(self, records: Iterable[Dict[str, Any]]) -> None:
        self._records = records
        self._validation_pipeline = self.create_validation_pipeline()

    def get_error_summary(self) -> Dict[str, int]:
        error_summary = {}
        for validator in [self.renaming_validator, self.cleanup_validator, self.record_validator]:
            for error in validator.invalid:
                error_type = error['error_type']
                error_summary[error_type] = error_summary.get(error_type, 0) + 1
        return error_summary
