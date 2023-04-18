# Ohio Fields

## Overview
Below are the fields that are available for Ohio.  The fields are grouped by the section of the voter file they are in.

## Ohio TOML Voter File Fields
``` toml 
[PERSON-DETAILS]
    [PERSON-DETAILS.voter-info]
        vuid = 'SOS_VOTERID'
        registration_date = 'REGISTRATION_DATE'
        registration_status = 'VOTER_STATUS'
        political_party = 'PARTY_AFFILIATION'
        dob = 'DATE_OF_BIRTH'
    [PERSON-DETAILS.name]
        last = 'LAST_NAME'
        first= 'FIRST_NAME'
        middle = 'MIDDLE_NAME'
        suffix = 'SUFFIX'
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
                zip4 = ''
            [PERSON-DETAILS.ADDRESS.mail]
                address1 = 'MAILING_ADDRESS1'
                address2 = 'MAILING_SECONDARY_ADDRESS'
                city = 'MAILING_CITY'
                state = 'MAILING_STATE'
                zip5 = 'MAILING_ZIP'
                zip4 = 'MAILING_ZIP_PLUS4'
                country = 'MAILING_COUNTRY'
                postal_code = 'MAILING_POSTAL_CODE'
        [PERSON-DETAILS.VOTING-DISTRICTS]
            municipal_court_district = 'MUNICIPAL_COURT_DISTRICT'
            court_of_appeals = 'COURT_OF_APPEALS'
            local_school_district = 'LOCAL_SCHOOL_DISTRICT'
                [PERSON-DETAILS.VOTING-DISTRICTS.precinct]
                    name = 'PRECINCT_NAME'
                    code = 'PRECINCT_CODE'
                [PERSON-DETAILS.VOTING-DISTRICTS.city]
                    name = 'CITY'
                    school_district = 'CITY_SCHOOL_DISTRICT'

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
        primary.march = ['PRIMARY-03/07/2000']
        general.november = ['GENERAL-11/07/2000']
    [ELECTION-DATES.Y2001]
        special.may = ['SPECIAL-05/08/2001']
        general.november = ['GENERAL-11/06/2001']
    [ELECTION-DATES.Y2002]
        primary.may = ['PRIMARY-05/07/2002']
        general.november = ['GENERAL-11/05/2002']
    [ELECTION-DATES.Y2003]
        special.may = ['SPECIAL-05/06/2003']
        general.november = ['GENERAL-11/04/2003']
    [ELECTION-DATES.Y2004]
        primary.march = ['PRIMARY-03/02/2004']
        general.november = ['GENERAL-11/02/2004']
    [ELECTION-DATES.Y2005]
        special.february = ['SPECIAL-02/08/2005']
        primary.may = ['PRIMARY-05/03/2005']
        primary.september = ['PRIMARY-09/13/2005']
        general.november = ['GENERAL-11/08/2005']
    [ELECTION-DATES.Y2006]
        special.february = ['SPECIAL-02/07/2006']
        primary.may = ['PRIMARY-05/02/2006']
        general.november = ['GENERAL-11/07/2006']
    [ELECTION-DATES.Y2007]
        primary.may = ['PRIMARY-05/08/2007']
        primary.september = ['PRIMARY-09/11/2007']
        general.november = ['GENERAL-11/06/2007']
        primary.november = ['PRIMARY-11/06/2007']
        general.december = ['GENERAL-12/11/2007']
    [ELECTION-DATES.Y2008]
        primary.march = ['PRIMARY-03/04/2008']
        primary.october = ['PRIMARY-10/14/2008']
        general.november = ['GENERAL-11/04/2008', 'GENERAL-11/18/2008']
    [ELECTION-DATES.Y2009]
        primary.may = ['PRIMARY-05/05/2009']
        primary.september = ['PRIMARY-09/08/2009', 'PRIMARY-09/15/2009', 'PRIMARY-09/29/2009']
        general.november = ['GENERAL-11/03/2009']
    [ELECTION-DATES.Y2010]
        primary.may = ['PRIMARY-05/04/2010']
        primary.july = ['PRIMARY-07/13/2010']
        primary.september = ['PRIMARY-09/07/2010']
        general.november = ['GENERAL-11/02/2010']
    [ELECTION-DATES.Y2011]
        primary.may = ['PRIMARY-05/03/2011']
        primary.september = ['PRIMARY-09/13/2011']
        general.november = ['GENERAL-11/08/2011']
    [ELECTION-DATES.Y2012]
        primary.march = ['PRIMARY-03/06/2012']
        general.november = ['GENERAL-11/06/2012']
    [ELECTION-DATES.Y2013]
        primary.may = ['PRIMARY-05/07/2013']
        primary.september = ['PRIMARY-09/10/2013']
        primary.october = ['PRIMARY-10/01/2013']
        general.november = ['GENERAL-11/05/2013']
    [ELECTION-DATES.Y2014]
        primary.may = ['PRIMARY-05/06/2014']
        general.november = ['GENERAL-11/04/2014']
    [ELECTION-DATES.Y2015]
        primary.may = ['PRIMARY-05/05/2015']
        primary.september = ['PRIMARY-09/15/2015']
        general.november = ['GENERAL-11/03/2015']
    [ELECTION-DATES.Y2016]
        primary.march = ['PRIMARY-03/15/2016']
        general.june = ['GENERAL-06/07/2016']
        primary.september = ['PRIMARY-09/13/2016']
        general.november = ['GENERAL-11/08/2016']
    [ELECTION-DATES.Y2017]
        primary.may = ['PRIMARY-05/02/2017']
        primary.september = ['PRIMARY-09/12/2017']
        general.november = ['GENERAL-11/07/2017']
    [ELECTION-DATES.Y2018]
        primary.may = ['PRIMARY-05/08/2018']
        general.august = ['GENERAL-08/07/2018']
        general.november = ['GENERAL-11/06/2018']
    [ELECTION-DATES.Y2019]
        primary.may = ['PRIMARY-05/07/2019']
        primary.september = ['PRIMARY-09/10/2019']
        general.november = ['GENERAL-11/05/2019']
    [ELECTION-DATES.Y2020]
        primary.march = ['PRIMARY-03/17/2020']
        general.november = ['GENERAL-11/03/2020']
    [ELECTION-DATES.Y2021]
        primary.may = ['PRIMARY-05/04/2021']
        primary.august = ['PRIMARY-08/03/2021']
        primary.september = ['PRIMARY-09/14/2021']
        general.november = ['GENERAL-11/02/2021']
    [ELECTION-DATES.Y2022]
        primary.may = ['PRIMARY-05/03/2022']
        primary.august = ['PRIMARY-08/02/2022']
        general.november = ['GENERAL-11/08/2022']

[PARTY-AFFILIATIONS]
C = 'Constitution Party'
D = 'Democrat Party'
E = 'Reform Party'
G = 'Green Party'
L = 'Libertarian Party'
N = 'Natural Law Party'
R = 'Republican Party'
S = 'Socialist Party'
X = 'Voted without declaring party affiliation'

```