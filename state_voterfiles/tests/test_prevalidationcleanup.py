import hypothesis
from hypothesis import given, strategies as st
from pydantic import ValidationError

from state_voterfiles.utils.pydantic_models.cleanup_model import PreValidationCleanUp, RecordRenamer

# Define strategies for different field types
name_strategy = st.builds(
    dict,
    first_name=st.text(min_size=1, max_size=50),
    last_name=st.text(min_size=1, max_size=50),
    middle_name=st.text(max_size=50).filter(lambda x: x != ''),
    suffix=st.sampled_from(['', 'Jr.', 'Sr.', 'III', 'IV']),
    gender=st.sampled_from(['M', 'F', 'O', '']),
)

address_strategy = st.builds(
    dict,
    address_line1=st.text(min_size=1, max_size=100),
    city=st.text(min_size=1, max_size=50),
    state=st.text(min_size=2, max_size=2),
    zip_code=st.text(min_size=5, max_size=10),
)

voter_registration_strategy = st.builds(
    dict,
    vuid=st.text(min_size=5, max_size=20),
    edr=st.dates(),
    status=st.sampled_from(['ACTIVE', 'INACTIVE', 'SUSPENDED', 'CANCELLED']),
    county=st.text(min_size=1, max_size=50),
)

# Create a strategy for RecordRenamer
record_renamer_strategy = st.builds(
    RecordRenamer,
    person_name_first_name=st.text(min_size=1, max_size=50),
    person_name_last_name=st.text(min_size=1, max_size=50),
    residential_address_line1=st.text(min_size=1, max_size=100),
    residential_city=st.text(min_size=1, max_size=50),
    residential_state=st.text(min_size=2, max_size=2),
    residential_zip_code=st.text(min_size=5, max_size=10),
    voter_vuid=st.text(min_size=5, max_size=20),
    voter_registration_date=st.dates(),
    voter_status=st.sampled_from(['ACTIVE', 'INACTIVE', 'SUSPENDED', 'CANCELLED']),
    voter_county=st.text(min_size=1, max_size=50),
)

@given(record_renamer_strategy)
def test_pre_validation_clean_up(record_renamer):
    try:
        clean_up = PreValidationCleanUp(data=record_renamer)

        # Test that essential fields are present
        assert clean_up.name is not None
        assert clean_up.name.first == record_renamer.person_name_first_name
        assert clean_up.name.last == record_renamer.person_name_last_name

        # Test that at least one address is present
        assert len(clean_up.address_list) > 0
        assert clean_up.address_list[0].address1 == record_renamer.residential_address_line1
        assert clean_up.address_list[0].city == record_renamer.residential_city
        assert clean_up.address_list[0].state == record_renamer.residential_state
        assert clean_up.address_list[0].zipcode == record_renamer.residential_zip_code

        # Test voter registration
        if clean_up.voter_registration:
            assert clean_up.voter_registration.vuid == record_renamer.voter_vuid
            assert clean_up.voter_registration.edr == record_renamer.voter_registration_date
            assert clean_up.voter_registration.status == record_renamer.voter_status
            assert clean_up.voter_registration.county == record_renamer.voter_county

    except ValidationError as e:
        # If a ValidationError is raised, make sure it's for a valid reason
        # You might want to add more specific checks here based on your validation rules
        print(f"ValidationError occurred: {e}")
        assert False, "Unexpected ValidationError"

# You can add more specific tests for other methods and edge cases

@given(st.builds(
    RecordRenamer,
    person_name_first_name=st.just(""),
    person_name_last_name=st.just(""),
))
def test_missing_name(record_renamer):
    with hypothesis.raises(ValidationError):
        PreValidationCleanUp(data=record_renamer)

@given(st.builds(
    RecordRenamer,
    residential_address_line1=st.just(""),
    residential_city=st.just(""),
    residential_state=st.just(""),
    residential_zip_code=st.just(""),
))
def test_missing_address(record_renamer):
    with hypothesis.raises(ValidationError):
        PreValidationCleanUp(data=record_renamer)

# Add more tests for other methods and edge cases as needed