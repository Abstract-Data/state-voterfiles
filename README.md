# Texas Ethics Commission Search

A simple script to search the Texas Ethics Commission's database of campaign contributions and expenditures.



## TEC Contribution Validator
The tec_contribution_validator.py script contains a validator class TECContributionValidator that validates contribution records according to the Texas Ethics Commission (TEC) filing requirements.

The TECContributionValidator class has several methods that validate different fields in a contribution record, including validate_contributor_name, validate_amount, validate_date, validate_occupation, validate_employer, and validate_address.

Each method checks that the field is present and valid according to the TEC's guidelines. For example, the validate_contributor_name method checks that the name is present and does not exceed the TEC's length limit for names. The validate_amount method checks that the amount is present and greater than zero. The validate_date method checks that the date is present and formatted correctly.

If a validation error is detected, the method raises a ValidationError with a descriptive error message.

The TECContributionValidator class also has a validate method that calls each of the above validation methods for a given contribution record. If any validation error is detected, the method raises a ValidationError with a summary of all the errors.

Overall, the TECContributionValidator class provides a way to ensure that contribution records conform to the TEC's filing requirements, helping to ensure compliance and accuracy in political campaign finance reporting.


## Record Key Generator
This script defines a data class RecordKeyGenerator that generates unique identifiers for records based on a combination of a hash and a UUID.

### Class Attributes
record: a string representing the record for which a unique identifier is being generated.
hash: the hexadecimal representation of the hash generated by the generate_hash() method.
uid: the UUID generated by the generate_uuid() method.
__KEY_LENGTH: the length of the generated hash. It is a class constant with a default value of 16.
### Class Methods
generate_hash(): generates a hash of the record attribute using the blake2b algorithm and updates the hash attribute with the hexadecimal representation of the hash.
generate_uuid(): generates a UUID and updates the uid attribute.
__post_init__(): automatically called after the object is initialized. Calls both generate_hash() and generate_uuid() methods.
### Example Usage
```
from app.validators.record_key_generator import RecordKeyGenerator
record = "Example Record"
key_generator = RecordKeyGenerator(record)
print(key_generator.hash) # "1d60c6ea90f6c31e"
print(key_generator.uid) # "6e4962cf-1933-4253-945f-31a28df984c5"
```
This creates a RecordKeyGenerator object with the record attribute set to "Example Record", generates the hash and UUID using the generate_hash() and generate_uuid() methods respectively, and prints the resulting hash and UUID.