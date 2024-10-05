# from __future__ import annotations
# from typing import Optional, Dict, Any, List
# from sqlalchemy import String, JSON, Integer, ForeignKey, Column, Enum, UniqueConstraint, and_
# from sqlalchemy.orm import relationship, mapped_column, Mapped, declarative_base
# from sqlalchemy.ext.declarative import declared_attr
# from sqlalchemy.ext.associationproxy import association_proxy
# import enum
#
# from state_voterfiles.utils.db_models.model_bases import Base
# from state_voterfiles.utils.db_models.fields.phone_number import ValidatedPhoneNumberModel
# from state_voterfiles.utils.db_models.fields.vendor import VendorNameModel
# from state_voterfiles.utils.db_models.fields.district import DistrictModel
# from state_voterfiles.utils.db_models.fields.address import AddressModel
#
#
# class AssociationType(enum.Enum):
#     DISTRICT = "district"
#     PHONE = "phone"
#     ADDRESS = "address"
#     VENDOR = "vendor"
#
#
# class GenericAssociationModel(Base):
#     __abstract__ = True
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     association_type: Mapped[AssociationType] = mapped_column(Enum(AssociationType), nullable=False)
#     associated_id: Mapped[int] = mapped_column(Integer, nullable=False)
#     record_type: Mapped[str] = mapped_column(String, nullable=False)
#     record_id: Mapped[int] = mapped_column(Integer, nullable=False)
#
#     __table_args__ = (
#         UniqueConstraint('association_type', 'associated_id', 'record_type', 'record_id'),
#     )
#
#     @declared_attr
#     def associated_object(cls):
#         return association_proxy('association', 'associated',
#                                  creator=lambda associated: AssociationModel(associated=associated))
#
#
#     @declared_attr
#     def association(cls):
#         return relationship(AssociationModel, uselist=False, cascade="all, delete-orphan")
#
#
# class AssociationModel(Base):
#     __tablename__ = 'associations'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     generic_association_id: Mapped[int] = mapped_column(ForeignKey('generic_associations.id'), nullable=False)
#     associated_type: Mapped[str] = mapped_column(String, nullable=False)
#
#     __mapper_args__ = {
#         'polymorphic_on': associated_type,
#     }
#
#
# class AddressAssociationModel(AssociationModel):
#     __tablename__ = 'address_associations'
#
#     id: Mapped[int] = mapped_column(ForeignKey('associations.id'), primary_key=True)
#     address_id: Mapped[int] = mapped_column(ForeignKey('addresses.id'), nullable=False)
#     associated: Mapped['AddressModel'] = relationship('AddressModel')
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'address',
#     }
#
#
# class DistrictAssociationModel(AssociationModel):
#     __tablename__ = 'district_associations'
#
#     id: Mapped[int] = mapped_column(ForeignKey('associations.id'), primary_key=True)
#     district_id: Mapped[int] = mapped_column(ForeignKey('districts.id'), nullable=False)
#     associated: Mapped['DistrictModel'] = relationship('DistrictModel')
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'district',
#     }
#
#
# class PhoneNumberAssociationModel(AssociationModel):
#     __tablename__ = 'phone_number_associations'
#
#     id: Mapped[int] = mapped_column(ForeignKey('associations.id'), primary_key=True)
#     phone_number_id: Mapped[int] = mapped_column(ForeignKey('phone_numbers.id'), nullable=False)
#     associated: Mapped['ValidatedPhoneNumberModel'] = relationship('ValidatedPhoneNumberModel')
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'phone',
#     }
#
#
# class VendorAssociationModel(AssociationModel):
#     __tablename__ = 'vendor_associations'
#
#     id: Mapped[int] = mapped_column(ForeignKey('associations.id'), primary_key=True)
#     vendor_id: Mapped[int] = mapped_column(ForeignKey('vendors.id'), nullable=False)
#     associated: Mapped['VendorNameModel'] = relationship('VendorNameModel')
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'vendor',
#     }
#
#
# class GenericAssociationMixin:
#     @declared_attr
#     def associations(cls):
#         return relationship(
#             GenericAssociationModel,
#             primaryjoin=lambda: and_(
#                 GenericAssociationModel.record_type == cls.__name__,
#                 GenericAssociationModel.record_id == cls.id
#             ),
#             cascade="all, delete-orphan"
#         )
#
#     @property
#     def districts(self):
#         return [
#             assoc.associated_object for assoc in self.associations if assoc.association_type == AssociationType.DISTRICT
#         ]
#
#     @property
#     def addresses(self):
#         return [
#             assoc.associated_object for assoc in self.associations if assoc.association_type == AssociationType.ADDRESS
#         ]
#
#     @property
#     def phone_numbers(self):
#         return [
#             assoc.associated_object for assoc in self.associations if assoc.association_type == AssociationType.PHONE
#         ]
#
#     @property
#     def vendors(self):
#         return [
#             assoc.associated_object for assoc in self.associations if assoc.association_type == AssociationType.VENDOR
#         ]
#
#     def add_address(self, address: 'AddressModel'):
#         assoc = GenericAssociationModel(association_type=AssociationType.ADDRESS, record_type=self.__class__.__name__)
#         assoc.associated_object = address
#         self.associations.append(assoc)
#
#     def add_district(self, district: 'DistrictModel'):
#         assoc = GenericAssociationModel(association_type=AssociationType.DISTRICT, record_type=self.__class__.__name__)
#         assoc.associated_object = district
#         self.associations.append(assoc)
#
#     def add_phone_number(self, phone_number: 'ValidatedPhoneNumberModel'):
#         assoc = GenericAssociationModel(association_type=AssociationType.PHONE, record_type=self.__class__.__name__)
#         assoc.associated_object = phone_number
#         self.associations.append(assoc)
#
#     def add_vendor(self, vendor: 'VendorNameModel'):
#         assoc = GenericAssociationModel(association_type=AssociationType.VENDOR, record_type=self.__class__.__name__)
#         assoc.associated_object = vendor
#         self.associations.append(assoc)
#
#     def remove_address(self, address: 'AddressModel'):
#         self.associations = [
#             assoc for assoc in self.associations
#             if not (assoc.association_type == AssociationType.ADDRESS and assoc.associated_object == address)
#         ]
#
#     def remove_district(self, district: 'DistrictModel'):
#         self.associations = [
#             assoc for assoc in self.associations
#             if not (assoc.association_type == AssociationType.DISTRICT and assoc.associated_object == district)
#         ]
#
#     def remove_phone_number(self, phone_number: 'ValidatedPhoneNumberModel'):
#         self.associations = [
#             assoc for assoc in self.associations
#             if not (assoc.association_type == AssociationType.PHONE and assoc.associated_object == phone_number)
#         ]
#
#     def remove_vendor(self, vendor: 'VendorNameModel'):
#         self.associations = [
#             assoc for assoc in self.associations
#             if not (assoc.association_type == AssociationType.VENDOR and assoc.associated_object == vendor)
#         ]