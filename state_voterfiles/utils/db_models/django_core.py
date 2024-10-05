# import abc
#
# from django.db import models
# from django.core.validators import RegexValidator
# from django.contrib.contenttypes.fields import GenericRelation
#
# from state_voterfiles.utils.db_models.model_bases import AbstractModelBase
#
#
# class AddressType(models.TextChoices):
#     MAILING = 'MAILING', 'Mailing'
#     RESIDENTIAL = 'RESIDENTIAL', 'Residential'
#     WORK = 'WORK', 'Work'
#     OTHER = 'OTHER', 'Other'
#
#
# class PhoneType(models.TextChoices):
#     MOBILE = 'MOBILE', 'Mobile'
#     HOME = 'HOME', 'Home'
#     WORK = 'WORK', 'Work'
#     OTHER = 'OTHER', 'Other'
#
#
# class DistrictType(models.TextChoices):
#     FEDERAL = 'FEDERAL', 'Federal'
#     STATE = 'STATE', 'State'
#     COUNTY = 'COUNTY', 'County'
#     CITY = 'CITY', 'City'
#     JUDICIAL = 'JUDICIAL', 'Judicial'
#     OTHER = 'OTHER', 'Other'
#
#
# class AbstractAddressModel(AbstractModelBase):
#     address_type = models.CharField(max_length=20, choices=AddressType.choices)
#     address1 = models.CharField(max_length=255, null=True, blank=True)
#     address2 = models.CharField(max_length=255, null=True, blank=True)
#     city = models.CharField(max_length=255, null=True, blank=True)
#     state = models.CharField(max_length=255, null=True, blank=True)
#     zipcode = models.CharField(max_length=255, null=True, blank=True)
#     zip5 = models.CharField(max_length=5, null=True, blank=True)
#     zip4 = models.CharField(max_length=4, null=True, blank=True)
#     county = models.CharField(max_length=255, null=True, blank=True)
#     country = models.CharField(max_length=255, null=True, blank=True)
#     standardized = models.CharField(max_length=255, null=True, blank=True)
#     address_parts = models.JSONField(null=True, blank=True)  # JSONField for storing a JSON object
#     address_key = models.CharField(max_length=255, null=True, blank=True)
#     is_mailing = models.BooleanField(null=True, blank=True)  # BooleanField equivalent to SQLAlchemy's Boolean
#     other_fields = models.JSONField(null=True, blank=True)  # Another JSONField for optional fields
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.Meta.unique_together = ['address1', 'address2', 'city', 'state', 'zipcode', 'content_type', 'object_id']
#         self.Meta.indexes.append(models.Index(fields=['content_type', 'object_id']))
#
#     def __str__(self):
#         return f"{self.standardized}"
#
#
# class AbstractValidatedPhoneNumberModel(AbstractModelBase):
#     phone_type = models.CharField(max_length=20, choices=PhoneType.choices, default=PhoneType.OTHER)
#     phone = models.CharField(max_length=20, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])
#     areacode = models.CharField(max_length=3)
#     number = models.CharField(max_length=7)
#     reliability = models.CharField(max_length=255, null=True, blank=True)
#     other_fields = models.JSONField(default=dict, blank=True, null=True)
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.Meta.indexes.append(models.Index(fields=['phone']))
#
#     def __str__(self):
#         return f"{self.get_phone_type_display()} phone for {self.content_object}: {self.phone}"
#
#
# class AbstractDistrictModel(AbstractModelBase):
#     state_abbv = models.CharField(max_length=2, null=True, blank=True)
#     city = models.CharField(max_length=100, null=True, blank=True)
#     county = models.CharField(max_length=100, null=True, blank=True)
#     type = models.CharField(max_length=50)
#     name = models.CharField(max_length=100, null=True, blank=True)
#     number = models.CharField(max_length=50, null=True, blank=True)
#     attributes = models.JSONField(default=dict)
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.Meta.indexes.append(models.Index(fields=['state_abbv', 'type', 'city', 'county']))
#         self.Meta.unique_together = ['state_abbv', 'type', 'name', 'number']
#
#     def __str__(self):
#         return f"{self.name} ({self.get_type_display()}) - {self.state_abbv}"
#
#
# class AbstractVendorNameModel(AbstractModelBase):
#     name = models.CharField(max_length=255, null=False)
#     tags = GenericRelation('VendorTagsModel')
#
#     def __str__(self):
#         return self.name
#
#
# class AbstractVendorTagsModel(AbstractModelBase):
#     tags = models.JSONField()
#     vendor = models.ForeignKey(AbstractVendorNameModel, on_delete=models.CASCADE, related_name='vendor_tag_relations')
#
#
#     def __str__(self):
#         return f"Tags for {self.vendor.name} on {self.content_object}"
#
#
# class AbstractDataSource(AbstractModelBase):
#     file = models.CharField(max_length=255)
#     processed_date = models.DateField(auto_now_add=True)
#
#     def __init__(self, **data):
#         super().__init__(**data)
#         self.Meta.unique_together = ['file', 'processed_date']
#         self.Meta.indexes.append(
#             [
#                 models.Index(fields=['file']),
#                 models.Index(fields=['processed_date'])
#             ]
#         )
#
#     def __str__(self):
#         return f"{self.file} ({self.processed_date})"
