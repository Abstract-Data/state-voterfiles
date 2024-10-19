from dataclasses import field, dataclass
from typing import Tuple, Iterable, Dict, Any, Optional, Generator

from sqlmodel import SQLModel, Relationship, Field as SQLModelField
from sqlalchemy.orm import configure_mappers
from state_voterfiles.utils.abcs.create_validator_abc import (
    CreateValidatorABC,
    RunValidationOutput,
    ErrorDetails
)
from state_voterfiles.utils.pydantic_models.rename_model import RecordRenamer
from state_voterfiles.utils.pydantic_models.cleanup_model import (
    PreValidationCleanUp,
    PersonName,
    VendorName,
    VendorTags,
    VendorTagsToVendorToRecordLink,
    VendorTagsToVendorLink,
    VoterRegistration,
    Address,
    AddressLink,
    ValidatedPhoneNumber,
    ElectionTypeDetails,
    ElectionVoteMethod,
    DataSource,
    DataSourceLink,
    District,
    InputData,
    VEPMatch,
    PhoneLink
)
from state_voterfiles.utils.db_models.record import RecordBaseModel
from state_voterfiles.utils.pydantic_models.table_manager import TableManager


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
    cleanup_validator: PreValidationCleanUp | CleanUpRecordValidator = field(default=PreValidationCleanUp)
    _records: Optional[Iterable[Dict[str, Any]]] = field(default=None, init=False)
    _validation_pipeline: Optional[Generator[RunValidationOutput, None, None]] = field(default=None, init=False)

    def __post_init__(self):
        self._set_table_names()
        self.renaming_validator = RecordRenameValidator(self.state_name, self.renaming_validator)
        self.record_validator = FinalValidation(self.state_name, self.record_validator)
        self.cleanup_validator = CleanUpRecordValidator(self.state_name, self.cleanup_validator)

    @property
    def valid(self) -> Generator[SQLModel, None, None]:
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

    def _set_table_names(self):
        for table_name, table in SQLModel.metadata.tables.items():
            old_name = table.name
            new_name = f"voterfile_{old_name}"
            table.name = new_name

    def validate_single_record(self, record: Dict[str, Any]) -> Generator[Tuple[str, Any], None, None]:
        renamed_record_gen = self.renaming_validator.validate_single_record(record)
        renamed_result = next(renamed_record_gen)
        if renamed_result[0] == 'valid':
            renamed_dict = dict(renamed_result[1])
            renamed_dict['data'] = renamed_result[1]
            cleaned_record_gen = self.cleanup_validator.validate_single_record(renamed_dict)
            cleaned_result = next(cleaned_record_gen)
            if cleaned_result[0] == 'valid':
                # # self._handle_collected_groups(cleaned_result)
                # final_record_gen = self.record_validator.validate_single_record(dict(cleaned_result[1]))
                # final_result = next(final_record_gen)
                # _container.final_model = final_result[1]
                yield "valid", cleaned_result[1]
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

    def create_validation_pipeline(self) -> Generator[RunValidationOutput, None, None]:
        if self._records is None:
            raise ValueError("run_validation must be called before creating the validation pipeline")

        # with ThreadPoolExecutor() as executor:
        #     futures = [executor.submit(self.validate_single_record, record) for record in self._records]
        #     for future in as_completed(futures):
        #         yield from future.result()

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
