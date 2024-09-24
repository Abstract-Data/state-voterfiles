# from typing import Set
#
# from pydantic import Field as PydanticField
#
# from state_voterfiles.utils.abcs.validation_model_abcs import FileCategoryListABC
#
#
# class FilePhoneNumberList(FileCategoryListABC):
#     phone_numbers: Set['ValidatedPhoneNumber'] = PydanticField(default_factory=set)
#
#     def add_or_update(self, new_phone_number: 'ValidatedPhoneNumber'):
#         for existing_phone_number in self.phone_numbers:
#             if existing_phone_number.id == new_phone_number.id:
#                 existing_phone_number.update(new_phone_number)
#                 return
#         self.phone_numbers.add(new_phone_number)
