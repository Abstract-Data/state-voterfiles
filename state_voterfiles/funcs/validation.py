import state_voterfiles.validatiors.validator_template as vt
from dataclasses import dataclass, field


@dataclass
class RecordValidator:
    record: dict

    @property
    def validated(self):
        return vt.RecordValidator(
            **self.record,
            sec_of_state=vt.SOSInfo(**self.record),
            voter_details=vt.PersonDetails(**self.record),
            address=vt.AllAddresses(
                raddress=vt.RegisteredAddress(**self.record),
                raddress_parts=vt.RegisteredAddressParts(**self.record),
                maddress=vt.MailingAddress(**self.record),
            ),
            districts=vt.AllDistricts(
                precinct=vt.VotingPrecinct(**self.record),
                city=vt.CityDistricts(**self.record),
                court=vt.CourtDistricts(**self.record),
                county=vt.CountyDistricts(**self.record),
                state=vt.StateDistricts(**self.record),
                federal=vt.FederalDistricts(**self.record)
            )
        )


@dataclass
class ValidateFile:
    data: list
    results: dict = field(init=False)

    def validate(self):
        valid, invalid = [], []
        for each in self.data:
            try:
                r = RecordValidator(each)
                valid.append(r.validated)
            except vt.ValidationError as e:
                invalid.append({'error': e,
                                'record': each})

        self.results = {'valid': valid,
                        'invalid': invalid}

        if len(valid) == len(self.data):
            print('All records are valid')
        else:
            print(f'{len(invalid):,} of {len(self.data):,} records are invalid')

        return self.results

