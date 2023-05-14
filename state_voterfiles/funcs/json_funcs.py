import pandas as pd
from typing import List, Dict


def flatten_json(json_data: List[Dict]) -> pd.DataFrame:
    """
    Flatten a nested json file into a pandas DataFrame.

    :param json_data: json data to flatten
    :return: pandas DataFrame
    """
    return pd.json_normalize(json_data)
