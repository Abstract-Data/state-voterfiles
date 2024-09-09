import csv
from pathlib import Path
from typing import Generator, Dict, Any, overload, Union, Callable
from datetime import datetime
from icecream import ic
from io import StringIO
import chardet
from collections import Counter
import string
# import logfire


ENABLE_LOGGING = False


# @logfire.no_auto_trace
def clean_filename(filename: str, max_length: int = 63) -> str:
    # Ensure the string contains only ASCII characters
    filename = ''.join(char for char in filename if char in string.ascii_letters + string.digits)
    # Truncate the string to the max_length
    return filename[:max_length]


# @logfire.no_auto_trace
# def create_record_counter(desc: Path) -> logfire.metric_counter:
#     filename_str = str(desc) if isinstance(desc, Path) else desc
#     _file = clean_filename(filename_str)
#     return logfire.metric_counter(f"{_file}_records_read")


# @logfire.no_auto_trace
def detect_file_encoding(file: Path):
    ic.configureOutput(prefix='detect_file_encoding()|') if ENABLE_LOGGING else ic.disable()
    _multiplier = 1
    confidence = 0
    _file_size_mb = file.stat().st_size / 1024 / 1024
    read_size = 65536 * 5  # Initial read size of 64KB
    total_read = 0

    with open(file, 'rb') as f:
        while confidence < 1.0 and total_read < _file_size_mb * 1024 * 1024:
            sample = f.read(read_size)
            total_read += len(sample)
            if not sample:  # Break if end of file is reached
                break
            result = chardet.detect(sample)
            confidence = result['confidence']
            ic(f"File:  {file.name} \r"
               f"Detected encoding: {result['encoding']} \r"
               f"Confidence level:  {confidence:.2%}. \r"
               f"File size read:    {total_read / 1024 / 1024:.2f} MB. ({total_read / (_file_size_mb * 1024 * 1024):.2%}) \r"
               f"Continuing to analyze the file.") if ENABLE_LOGGING else ic.disable()
            read_size *= _multiplier  # Increase read size for the next iteration
            _multiplier *= 10  # Exponentially increase the multiplier

        ic(f"Detected encoding: {result['encoding']}") if ENABLE_LOGGING else ic.disable()
    return result['encoding']


# @logfire.no_auto_trace
def detect_delimiter(file_path: Path, num_lines: int = 10) -> str:
    ic.configureOutput(prefix='detect_delimiter()|') if ENABLE_LOGGING else ic.disable()
    common_delimiters = [',', '\t', ';', '|']
    delimiter_counts = {delimiter: 0 for delimiter in common_delimiters}

    # Detect the file encoding first
    file_encoding = detect_file_encoding(file_path)

    with open(file_path, 'r', encoding=file_encoding) as file:
        lines = [file.readline() for _ in range(num_lines)]

    for line in lines:
        line_counts = Counter(line)
        for delimiter in common_delimiters:
            delimiter_counts[delimiter] += line_counts[delimiter]

    detected_delimiter = max(delimiter_counts, key=delimiter_counts.get)
    ic(f"Detected delimiter for {file_path.name}: {detected_delimiter}") if ENABLE_LOGGING else ic.disable()
    return detected_delimiter


# @logfire.no_auto_trace
def clean_and_read_csv(file_path: Path, delimiter=',', **csv_kwargs) -> Generator[Dict[str, Any], None, None]:
    with open(file_path, 'rb') as file:
        content = file.read().replace(b'\x00', b'')
    cleaned_content = StringIO(content.decode(csv_kwargs.get("encoding", "utf-8")))
    reader = csv.DictReader(cleaned_content, delimiter=delimiter, **csv_kwargs)
    for row in reader:
        yield row


# @logfire.no_auto_trace
def include_file_origin(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        records = func(*args, **kwargs)
        for record in records:
            record["file_origin"] = Path(args[0]).stem
            yield record
    return wrapper


# @logfire.no_auto_trace
def include_file_date_created(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        records = func(*args, **kwargs)
        for record in records:
            record["created_at"] = Path(args[0]).stat().st_ctime
            yield record
    return wrapper


# @logfire.no_auto_trace
def include_file_date_imported(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        records = func(*args, **kwargs)
        for record in records:
            record["imported_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            yield record
    return wrapper


@overload
def read_csv(file: str, **kwargs):
    ...


@overload
def read_csv(file: Path, **kwargs):
    ...


@include_file_origin
@include_file_date_created
@include_file_date_imported
def read_csv(file: Union[str, Path], **kwargs) -> Generator[Dict[str, Any], None, None]:
    ic.configureOutput(prefix='read_csv()|') if ENABLE_LOGGING else ic.disable()
    if isinstance(file, str):
        file = Path(file)

    # _log = logfire.span(f"Reading {file.name}")
    _encoding = kwargs.get("encoding", detect_file_encoding(file))
    _delim = kwargs.get("delimiter", detect_delimiter(file))
    _headers = kwargs.get("headers", None)
    _uppercase = kwargs.get("uppercase", False)
    _lowercase = kwargs.get("lowercase", False)
    _state = kwargs.get("state", None)
    # with _log:
    with open(file, "r", encoding=_encoding if _encoding != "ascii" else "utf-8", errors='ignore') as f:
        if file.suffix == ".txt":
            if _headers:
                reader = csv.DictReader(f, delimiter=_delim, fieldnames=_headers)
            else:
                reader = csv.DictReader(f, delimiter=_delim)
                first_row_header = next(reader)
                try:
                    reader = csv.DictReader(f, delimiter=_delim, fieldnames=first_row_header)
                except csv.Error:
                    reader = clean_and_read_csv(
                        file,
                        delimiter=_delim,
                        fieldnames=first_row_header,
                        encoding=_encoding
                    )
        elif file.suffix == ".csv":
            try:
                reader = csv.DictReader(f)
            except csv.Error:
                reader = clean_and_read_csv(
                    file,
                    delimiter=_delim
                )
        else:
            reader = None

        if reader:
            _counter = 0
            for record in reader:
                record = {k: v.upper() for k, v in record.items() if k}
                if _uppercase:
                    record = {k.upper(): v for k, v in record.items() if k}
                elif _lowercase:
                    record = {k.lower(): v for k, v in record.items() if k}
                if _state:
                    record["state"] = _state
                _counter += 1
                yield record
        # _log.set_attribute("records_read", f"{_counter:,}")
        # _log.set_attribute("file_origin", file.stem)
        # _log.set_attribute("file_path", file)
        # _log.set_attribute("file_size", file.stat().st_size)
