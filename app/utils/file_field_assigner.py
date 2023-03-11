from dataclasses import dataclass, field
from collections import namedtuple
from typing import Optional

@dataclass(repr=False)
class RecordDetails:
    name: str = field(init=False)
    person: namedtuple = field(init=False)
    company: namedtuple = field(init=False)
    address: namedtuple = field(init=False)
    employer: namedtuple = field(init=False)


@dataclass
class AddressDetails:
    address1: str
    address2: str
    city: str
    state: str
    zip5: str
    zip4: str
    county: str
    country: str


@dataclass
class PersonDetails:
    prefix: str
    title: str
    first_name: str
    middle_name: str
    last_name: str
    suffix: str
    formatted: str
    nickname: str


@dataclass
class CompanyDetails:
    name: str
    address: AddressDetails
    formatted: str


@dataclass
class DonorEmployerDetails:
    employer: str
    occupation: str
    jobtitle: str


def field_generator(category) -> RecordDetails:
    _name = category.get('name')
    _person = PersonDetails(
        prefix=category['person'].get('prefix'),
        title=category['person'].get('title'),
        first_name=category['person'].get('firstName'),
        middle_name=category['person'].get('middleName'),
        last_name=category['person'].get('lastName'),
        suffix=category['person'].get('suffix'),
        formatted=category['person'].get('formatted'),
        nickname=category['person'].get('nickname')
    ) if category.get('person') else None

    _company = CompanyDetails(
        name=category['company'].get('name'),
        formatted=category['company'].get('formatted'),
        address=AddressDetails(
            address1=category['company']['address'].get('address1'),
            address2=category['company']['address'].get('address2'),
            city=category['company']['address'].get('city'),
            state=category['company']['address'].get('state'),
            zip5=category['company']['address'].get('zip5'),
            zip4=category['company']['address'].get('zip4'),
            county=category['company']['address'].get('county'),
            country=category['company']['address'].get('country')
        ) if category['company'].get('address') else None


    ) if category.get('company') else None
    _address = AddressDetails(
        address1=category['address'].get('address1'),
        address2=category['address'].get('address2'),
        city=category['address'].get('city'),
        state=category['address'].get('state'),
        zip5=category['address'].get('zip5'),
        zip4=category['address'].get('zip4'),
        county=category['address'].get('county'),
        country=category['address'].get('country')
    ) if category.get('address') else None

    _employer = DonorEmployerDetails(
        employer=category['person'].get('employer'),
        occupation=category['person'].get('occupation'),
        jobtitle=category['person'].get('jobtitle'),
    ) if category.get('person') else None

    details = RecordDetails()
    if _name is not None:
        details.name = _name
    if _person is not None:
        details.person = _person
    if _company is not None:
        details.company = _company
    if _address is not None:
        details.address = _address
    if _employer.employer is not None:
        details.employer = _employer
    return details
