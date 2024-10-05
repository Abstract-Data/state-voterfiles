# import abc
#
# from django.db import models
# from django.contrib.contenttypes.fields import GenericRelation
# from .django_core import (
#     AbstractAddressModel,
#     AbstractValidatedPhoneNumberModel,
#     AbstractDistrictModel,
#     AbstractVendorNameModel,
#     AbstractVendorTagsModel,
#     AbstractModelBase
# )
#
#
# class AbstractPersonNameModel(AbstractModelBase):
#     prefix = models.CharField(max_length=10, null=True)
#     first = models.CharField(max_length=50)
#     last = models.CharField(max_length=50)
#     middle = models.CharField(max_length=50, null=True)
#     suffix = models.CharField(max_length=10, null=True)
#     dob = models.DateField
#     gender = models.CharField(max_length=1, null=True)
#     other_fields = models.JSONField(null=True)
#
#
# class AbstractVoterRegistrationModel(AbstractModelBase):
#     vuid = models.CharField(max_length=255, null=True, blank=True, unique=True)
#     edr = models.DateField(null=True, blank=True)
#     status = models.CharField(max_length=255, null=True, blank=True)
#     county = models.CharField(max_length=255, null=True, blank=True)
#     attributes = models.JSONField(null=True, blank=True)  # JSONField for storing attributes
#     # record = models.OneToOneField('RecordModel', on_delete=models.CASCADE, related_name='voter_registration_relation')
#
#
# class ElectionType(models.TextChoices):
#     GE = 'GE', 'GE'
#     PE = 'PE', 'PE'
#     ME = 'ME', 'ME'
#     SE = 'SE', 'SE'
#     RE = 'RE', 'RE'
#     PR = 'PR', 'PR'
#     OP = 'OP', 'OP'
#     CP = 'CP', 'CP'
#     NP = 'NP', 'NP'
#     SB = 'SB', 'SB'
#     JE = 'JE', 'JE'
#     LE = 'LE', 'LE'
#     CE = 'CE', 'CE'
#     RF = 'RF', 'RF'
#     PP = 'PP', 'PP'
#     PPR = 'PPR', 'PPR'
#     PC = 'PC', 'PC'
#
#
# class VoteMethod(models.TextChoices):
#     IP = 'IP', 'IP'
#     MI = 'MI', 'MI'
#     EV = 'EV', 'EV'
#     PV = 'PV', 'PV'
#     AB = 'AB', 'AB'
#
#
# class AbstractElectionTypeModel(AbstractModelBase):
#     year = models.IntegerField()
#     election_type = models.CharField(max_length=3, choices=ElectionType.choices)
#     state = models.CharField(max_length=2)
#     city = models.CharField(max_length=100, null=True, blank=True)
#     county = models.CharField(max_length=100, null=True, blank=True)
#     dates = models.JSONField(default=list, blank=True, null=True)
#     desc = models.TextField(null=True, blank=True)
#
#
# class AbstractVotedInElectionModel(AbstractModelBase):
#     party = models.CharField(max_length=50, null=True, blank=True)
#     vote_date = models.DateField(null=True, blank=True)
#     vote_method = models.CharField(max_length=2, choices=VoteMethod.choices)
#     # election = models.ForeignKey(AbstractElectionTypeModel, on_delete=models.CASCADE, related_name='voted_in_election')
#     # record = models.ForeignKey('RecordModel', on_delete=models.CASCADE, related_name='election_history')
#
#
# class AbstractVEPKeysModel(AbstractModelBase):
#     uuid = models.CharField(max_length=255, null=True, blank=True)
#     long = models.CharField(max_length=255, null=True, blank=True)
#     short = models.CharField(max_length=255, null=True, blank=True)
#     name_dob = models.CharField(max_length=255, null=True, blank=True)
#     addr_text = models.CharField(max_length=255, null=True, blank=True)
#     addr_key = models.CharField(max_length=255, null=True, blank=True)
#     full_key = models.CharField(max_length=255, null=True, blank=True)
#     full_key_hash = models.CharField(max_length=255, null=True, blank=True)
#     best_key = models.CharField(max_length=255, null=True, blank=True)
#     uses_mailzip = models.BooleanField(null=True, blank=True)
#
#     # record = models.OneToOneField('RecordModel', on_delete=models.CASCADE, related_name='vep_keys_relation')
#
#
# class AbstractInputDataModel(AbstractModelBase):
#     __abstract__ = True
#
#     original_data = models.JSONField(null=False)
#     renamed_data = models.JSONField(null=False)
#     corrections = models.JSONField(null=False)
#     settings = models.JSONField(null=False)
#     date_format = models.JSONField(null=False)
#     # record = models.OneToOneField('RecordModel', on_delete=models.CASCADE, related_name='input_data_relation')
#
#
# class AbstractRecordModel(AbstractModelBase):
#     name = GenericRelation(AbstractPersonNameModel, on_delete=models.SET_NULL, null=True, related_name='record')
#     voter_registration = GenericRelation(AbstractVoterRegistrationModel, on_delete=models.SET_NULL, null=True, related_name='record')
#     addresses = GenericRelation(AbstractAddressModel)
#     phone_numbers = GenericRelation(AbstractValidatedPhoneNumberModel)
#     districts = GenericRelation(AbstractDistrictModel)
#     elections = GenericRelation(AbstractElectionTypeModel, through='VotedInElectionModel', related_name='voters')
#     vote_history = GenericRelation(AbstractVotedInElectionModel)
#     vendors = GenericRelation(AbstractVendorNameModel, through='VendorTagsModel', related_name='records')
#     vendor_tags = GenericRelation(AbstractVendorTagsModel)
#     vep_keys = GenericRelation(AbstractVEPKeysModel, on_delete=models.SET_NULL, null=True, related_name='record')
#     input_data = GenericRelation(AbstractInputDataModel, on_delete=models.SET_NULL, null=True, related_name='record')
#     unassigned = models.JSONField(null=True, blank=True)
#     corrected_errors = models.JSONField(default=dict)
#
#     @abc.abstractmethod
#     def get_address(self, address_type):
#         return self.addresses.filter(address_type=address_type).first()
#
#     @property
#     @abc.abstractmethod
#     def mailing_address(self):
#         return self.get_address(AbstractAddressModel.address_type.MAILING)
#
#     @property
#     @abc.abstractmethod
#     def residential_address(self):
#         return self.get_address(AbstractAddressModel.address_type.RESIDENTIAL)
#
#     @abc.abstractmethod
#     def get_vendors(self):
#         return self.vendors.all()
#
#     @abc.abstractmethod
#     def get_vendor_tags(self, vendor):
#         tag_relation = self.vendor_tag_relations.filter(vendor=vendor).first()
#         return tag_relation.tags if tag_relation else None
#
#     @abc.abstractmethod
#     def add_address(self, **address_data):
#         return self.addresses.create(**address_data)
#
#     @abc.abstractmethod
#     def add_phone_number(self, **phone_data):
#         return self.phone_numbers.create(**phone_data)
#
#     @abc.abstractmethod
#     def add_district(self, **district_data):
#         return self.districts.create(**district_data)
#
#     @abc.abstractmethod
#     def add_vendor_tags(self, vendor, tags):
#         return AbstractVendorTagsModel.objects.update_or_create(
#             record=self,
#             vendor=vendor,
#             defaults={'tags': tags}
#         )
#
#     def __str__(self):
#         return f"Record {self.id}"
