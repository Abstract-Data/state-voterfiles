from typing import Dict, Any, List, Union
from pydantic_core import PydanticCustomError
from pydantic import AliasChoices
import re


def safe_dict_merge(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely merge any number of dictionaries, handling None values.

    Args:
        *dicts: Variable number of dictionaries to merge.

    Returns:
        A new dictionary containing all key-value pairs from the input dictionaries.
    """
    result = {}
    for d in dicts:
        if d is not None:
            result |= d  # This is equivalent to result.update(d) in Python 3.9+
    return result


def only_text_and_numbers(input_string):
    # Regex pattern to match non-numbers, non-letters, and non-spaces
    pattern = r'[^a-zA-Z0-9 ]'
    # Substitute the matched patterns with an empty string
    cleaned_string = re.sub(pattern, '', input_string)
    return cleaned_string


def next_with_key_suffix(k: str, dict_: Dict[str, Any]) -> bool:
    return next((value for key, value in dict_.items() if key.endswith(k) and value), None)


def key_list_with_suffix(sfx: str, dict_: Dict[str, Any]) -> List[str]:
    return [key for key in dict_.keys() if key.endswith(sfx)]


def value_list_with_prefix(dict_: Dict[str, Any], *args: Union[str, List[str], tuple]) -> List[str]:
    # Flatten the args if they are lists or tuples
    prefixes = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            prefixes.extend(arg)
        else:
            prefixes.append(arg)

    return [value for key, value in dict_.items() if any(key.startswith(prefix) for prefix in prefixes) and value]


def dict_with_prefix(pfx: str, dict_: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in dict_.items() if key.startswith(pfx) and value}


def getattr_with_prefix(pfx: str, obj: Any) -> Dict[str, Any]:
    return {key: getattr(obj, key) for key in dir(obj) if key.startswith(pfx) and getattr(obj, key)}


def remove_empty_from_dict(dict_: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in dict_.items() if value}


def remove_prefix(d: Dict[str, Any], prefixes: List[str]) -> Dict[str, Any]:
    if not any(d):
        raise PydanticCustomError(
            'remove_prefix_func',
            'Dictionary is empty',
            None
        )
    return {k.replace(pfx, ''): v for k, v in d.items() if v for pfx in prefixes}


def if_null_none(*args):
    if isinstance(args, str):
        if args not in ["", "null"]:
            return AliasChoices(args)
    if isinstance(args, list):
        _fields = [field for field in args if field not in ["", "null"]]
        return AliasChoices(*_fields)
    return None


def create_raw_data_dict(cls, values) -> Dict[str, Any]:
    _raw_values = values.copy()
    values['raw_data'] = _raw_values
    return values


def clear_blank_strings(cls, values) -> Dict[str, Any]:
    """
    Clear out all blank strings or ones that contain 'null' from records.
    :param cls:
    :param values:
    :return:
    """
    for k, v in values.items():
        if v in ["", '"', "null"]:
            values[k] = None
        if k in ["", '"', "null"]:
            values[k] = values[k].replace(k, None)
    return values
