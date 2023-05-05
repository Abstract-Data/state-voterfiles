
# TODO: Figure out the issues with why alias is not being assigned correctly to each field in ValidatorTemplate.
def assign_fields(x: dict) -> dict:
    return {
        'vuid': x['PERSON-DETAILS']['voter-info']['vuid'],
        'edr': x['PERSON-DETAILS']['voter-info']['registration_date'],
        'status': x['PERSON-DETAILS']['voter-info']['registration_status'],
        'lname': x['PERSON-DETAILS']['name']['last'],
        'fname': x['PERSON-DETAILS']['name']['first'],
        'mname': x['PERSON-DETAILS']['name']['middle'],
        'sfx': x['PERSON-DETAILS']['name']['suffix'],
        'dob': x['PERSON-DETAILS']['voter-info']['dob'],
        'radr1': x['PERSON-DETAILS']['ADDRESS']['residence']['address1'],
        'radr2': x['PERSON-DETAILS']['ADDRESS']['residence']['address2'],
        'rcity': x['PERSON-DETAILS']['ADDRESS']['residence']['city'],
        'rstate': x['PERSON-DETAILS']['ADDRESS']['residence']['state'],
        'rzip': x['PERSON-DETAILS']['ADDRESS']['residence']['zip5'],
        'rzip4': x['PERSON-DETAILS']['ADDRESS']['residence']['zip4'],
        'rcountry': x['PERSON-DETAILS']['ADDRESS']['residence']['country'],
        'rpostal_code': x['PERSON-DETAILS']['ADDRESS']['residence']['postal_code'],
        'rhnum': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['house_number'],
        'rdesig': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['house_direction'],
        'rstname': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['street_name'],
        'rsttype': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['street_type'],
        'rstsfx': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['street_suffix'],
        'runum': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['unit_number'],
        'rutype': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['unit_type'],
        # rcity' : x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['city'],
        # rstate' : x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['state'],
        # rzip': x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['zip'],
        # rzip4' x['PERSON-DETAILS']['ADDRESS']['parts']['residence']['zip4'],
        'maddr1': x['PERSON-DETAILS']['ADDRESS']['mail']['address1'],
        'maddr2': x['PERSON-DETAILS']['ADDRESS']['mail']['address2'],
        'mcity': x['PERSON-DETAILS']['ADDRESS']['mail']['city'],
        'mstate': x['PERSON-DETAILS']['ADDRESS']['mail']['state'],
        'mzip': x['PERSON-DETAILS']['ADDRESS']['mail']['zip5'],
        'mzip4': x['PERSON-DETAILS']['ADDRESS']['mail']['zip4'],
        'mcountry': x['PERSON-DETAILS']['ADDRESS']['mail']['country'],
        'mpostal_code': x['PERSON-DETAILS']['ADDRESS']['mail']['postal_code'],

        'municipal_court_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['municipal_court_district'],
        'court_of_appeals': x['PERSON-DETAILS']['VOTING-DISTRICTS']['court_of_appeals'],
        'local_school_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['local_school_district'],

        'precinct_name': x['PERSON-DETAILS']['VOTING-DISTRICTS']['precinct']['name'],
        'precinct_code': x['PERSON-DETAILS']['VOTING-DISTRICTS']['precinct']['code'],

        'city_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['city']['name'],
        'city_school_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['city']['school_district'],

        'county_district_number': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['number'],
        'county_district_id': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['id'],
        'county_district_township': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['township'],
        'county_district_village': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['village'],
        'county_district_ward': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['ward'],
        'county_district_library': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['library_district'],
        'county_district_career_center': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['career_center'],
        'county_district_court': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county']['court_district'],
        'county_district_education_service_center': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county'][
            'education_service_center'],
        'county_district_exempted_village_school_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['county'][
            'exempted_village_school_district'],

        'state_board_of_education': x['PERSON-DETAILS']['VOTING-DISTRICTS']['state']['board_of_edu'],
        'state_representative_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['state']['lower_chamber'],
        'state_senate_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['state']['upper_chamber'],

        'congressional_district': x['PERSON-DETAILS']['VOTING-DISTRICTS']['federal']['congressional'],

    }
