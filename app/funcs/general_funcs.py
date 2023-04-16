import pandas as pd
from pathlib import Path

func_path = Path(__file__).parent.parent.joinpath("pandas_schemas")

def uppercase(series: pd.Series) -> pd.Series:
    return series.str.strip().str.upper()


def pandas_datetime(series: pd.Series) -> pd.to_datetime:
    return pd.to_datetime(series)


def currency_format(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        df[column] = df[column].fillna(0)
        if df[column].dtype == 'float':
            df[column] = df[column].map(lambda x: f"${x:,.2f}")

    df = df.replace('$0.00', '')
    return df


def write_pandas_schema(df: pd.DataFrame, schema_name: str, file: str | Path = None) -> None:
    if not file:
        file = func_path
    import pandera as pa
    schema = pa.infer_schema(df)
    with open(file.joinpath(f"{schema_name}.py"), 'w') as f:
        f.write(schema.to_script())
        print(f"Schema written to {file.joinpath(f'{schema_name}.py')}")