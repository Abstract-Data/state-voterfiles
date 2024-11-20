from sqlmodel import Field as SQLModelField

from ...abcs.validation_model_abcs import FileCategoryListABC
from ..fields.vendor import VendorName


class FileVendorNameList(FileCategoryListABC):
    vendors: set[VendorName] = SQLModelField(default_factory=set)

    def add_or_update(self, new_vendor: VendorName):
        for existing_vendor in self.vendors:
            if existing_vendor.id == new_vendor.id:
                existing_vendor.update(new_vendor)
                return
        self.vendors.add(new_vendor)

    def generate_hash_key(self) -> str:
        return "_".join(sorted([x.id for x in self.vendors]))