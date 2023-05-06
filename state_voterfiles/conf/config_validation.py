
class ValidatorSettings:
    """Settings for pydantic validator."""
    orm_mode = True
    validate_assignment = True
    validate_all = True
    allow_mutation = True
    anystr_strip_whitespace = True
    allow_population_by_field_name = True
