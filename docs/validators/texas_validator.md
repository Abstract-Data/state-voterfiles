## TexasValidator
`TexasValidator` is a Pydantic model that represents the data format used by the Texas Secretary of State to store voter data. It includes fields for personal information such as name, date of birth, and address, as well as fields for voting history.

### Usage 
``` py 
from pydantic import ValidationError
from mymodule import TexasValidator

try:
    patient_data = TexasValidator.parse_raw(json_string)
except ValidationError as e:
    print(e)
else:
    # do something with voter_data
```

### Fields
- `VUID`: an integer between 0 and 999999999999
- `EDR`: a date string in the format YYYYMMDD  
- `STATUS`: a string representing the patient's status  
- `LNAME`: the patient's last name  
- `FNAME`: the patient's first name  
- `MNAME`: an optional string representing the patient's middle name
- `SFX`: an optional string representing the patient's suffix (e.g. Jr.)
- `DOB`: a date string in the format YYYYMMDD
- `SEX`: a string representing the patient's sex, either 'M', 'F', or 'U'
- `RHNUM`: an optional string representing the patient's blood type (e.g. A+)
- `RDESIG`: an optional string representing the patient's designation (e.g. Dr.)
- `RSTNAME`: an optional string representing the patient's street name
- `RSTTYPE`: an optional string representing the patient's street type (e.g. St.)
- `RSTSFX`: an optional string representing the patient's street suffix (e.g. Apt. 101)
- `RUNUM`: an optional string representing the patient's unit number (e.g. 101)
- `RUTYPE`: an optional string representing the patient's unit type (e.g. Apt.)
- `RCITY`: a string representing the patient's city
- `RSTATE`: a string representing the patient's state, defaulting to 'TX'
- `RZIP`: an integer between 0 and 99999 representing the patient's zip code
- `RZIP4`: an optional integer between 0 and 9999 representing the patient's zip+4 code
- `MADR1`: an optional string representing the patient's mailing address line 1
- `MADR2`: an optional string representing the patient's mailing address line 2
- `MCITY`: an optional string representing the patient's mailing address city
- `MST`: an optional string representing the patient's mailing address state
- `MZIP`: an optional integer between 0 and 99999 representing the patient's mailing address zip code
- `MZIP4`: an optional integer between 0 and 9999 representing the patient's mailing address zip+4 code
- `NEWHD`: an integer between 0 and 150 representing the patient's HD (hemodialysis) time in minutes
- `NEWSD`: an integer between 0 and 35 representing the patient's SD (sustained low efficiency dialysis) time in minutes
- `NEWCD`: an integer between 0 and 39 representing the patient's CD (continuous cycling peritoneal dialysis) time in minutes

### Configuration
`orm_mode = True`: tells Pydantic to ignore unknown fields when parsing the input data.  
`validate_assignment = True`: tells Pydantic to raise a validation error if an attribute is assigned an invalid value.  
`validate_all = True`: tells Pydantic to validate all fields, even optional ones

### Validators
`clear_blank_strings`: Clear all empty strings with only "" to `None`