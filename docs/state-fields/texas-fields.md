# Title: Texas Fields

## Overview 
Below are the fields that are available for Texas.  The fields are grouped by the section of the voter file they are in. 

## Texas TOML Voter File Fields
``` toml 
[PERSON-DETAILS]
[PERSON-DETAILS.voter-info]
vuid = 'VUID'
registration_date = 'EDR'
registration_status = 'STATUS'
political_party = ''
dob = 'DOB'
[PERSON-DETAILS.name]
last = 'LNAME'
first= 'FNAME'
middle = 'MNAME'
suffix = 'SFX'
[PERSON-DETAILS.ADDRESS]
[PERSON-DETAILS.ADDRESS.residence]
address1 = 'RESIDENTIAL_ADDRESS1'
address2 = 'RESIDENTIAL_SECONDARY_ADDR'
city = 'RESIDENTIAL_CITY'
state = 'RESIDENTIAL_STATE'
zip5 = 'RESIDENTIAL_ZIP'
zip4 = 'RESIDENTIAL_ZIP_PLUS4'
country = 'RESIDENTIAL_COUNTRY'
postal_code = 'RESIDENTIAL_POSTALCODE'
[PERSON-DETAILS.ADDRESS.parts.residence]
house_number = 'RHNUM'
house_direction = 'RDESIG'
street_name = 'RSTNAME'
street_type = 'RSTTYPE'
street_suffix = 'RSTSFX'
unit_number = 'RUNUM'
unit_type = 'RUTYPE'
city = 'RCITY'
state = 'TX'
zip = 'RZIP'
zip4 = 'RZIP4'
[PERSON-DETAILS.ADDRESS.mail]
address1 = 'MADR1'
address2 = 'MADR2'
city = 'MCITY'
state = 'MST'
zip5 = 'MZIP'
zip4 = 'MZIP4'
country = ''
postal_code = ''
[PERSON-DETAILS.VOTING-DISTRICTS]
municipal_court_district = ''
court_of_appeals = ''
local_school_district = ''
[PERSON-DETAILS.VOTING-DISTRICTS.precinct]
name = ''
code = ''
[PERSON-DETAILS.VOTING-DISTRICTS.city]
name = ''
school_district = ''

[PERSON-DETAILS.VOTING-DISTRICTS.county]
number = 'COUNTY_NUMBER'
id = 'COUNTY_ID'
township = 'TOWNSHIP'
village = 'VILLAGE'
ward = 'WARD'
library_district = 'LIBRARY'
career_center = 'CAREER_CENTER'
court_district = 'COUNTY_COURT_DISTRICT'
education_service_center = 'EDU_SERVICE_CENTER_DISTRICT'
exempted_village_school_district = 'EXEMPTED_VILL_SCHOOL_DISTRICT'
[PERSON-DETAILS.VOTING-DISTRICTS.state]
board_of_edu = 'STATE_BOARD_OF_EDUCATION'
lower_chamber = 'STATE_REPRESENTATIVE_DISTRICT'
upper_chamber = 'STATE_SENATE_DISTRICT'
[PERSON-DETAILS.VOTING-DISTRICTS.federal]
congressional = 'CONGRESSIONAL_DISTRICT'

[ELECTION-DATES]
[ELECTION-DATES.Y2000]
primary.march = ''
general.november = ''
[ELECTION-DATES.Y2001]
special.may = ''
general.november = ''
[ELECTION-DATES.Y2002]
primary.may = ''
general.november = ''
[ELECTION-DATES.Y2003]
special.may = ''
general.november = ''
[ELECTION-DATES.Y2004]
primary.march = ''
general.november = ''
[ELECTION-DATES.Y2005]
special.february = ''
primary.may = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2006]
special.february = ''
primary.may = ''
general.november = ''
[ELECTION-DATES.Y2007]
primary.may = ''
primary.september = ''
general.november = ''
primary.november = ''
general.december = ''
[ELECTION-DATES.Y2008]
primary.march = ''
primary.october = ''
general.november = ''
[ELECTION-DATES.Y2009]
primary.may = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2010]
primary.may = ''
primary.july = ''
general.november = ''
[ELECTION-DATES.Y2011]
primary.may = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2012]
primary.march = ''
general.november = ''
[ELECTION-DATES.Y2013]
primary.may = ''
primary.september = ''
primary.october = ''
general.november = ''
[ELECTION-DATES.Y2014]
primary.may = ''
general.november = ''
[ELECTION-DATES.Y2015]
primary.may = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2016]
primary.march = ''
general.june = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2017]
primary.may = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2018]
primary.may = ''
general.august = ''
general.november = ''
[ELECTION-DATES.Y2019]
primary.may = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2020]
primary.march = ''
general.november = ''
[ELECTION-DATES.Y2021]
primary.may = ''
primary.august = ''
primary.september = ''
general.november = ''
[ELECTION-DATES.Y2022]
primary.may = ''
primary.august = ''
general.november = ''

[PARTY-AFFILIATIONS]
C = ''
D = ''
E = ''
G = ''
L = ''
N = ''
R = ''
S = ''
X = ''
```