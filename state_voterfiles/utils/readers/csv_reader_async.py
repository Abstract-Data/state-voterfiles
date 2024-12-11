from __future__ import annotations
from dataclasses import dataclass
import csv
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Union, Callable, TypeVar, List
from datetime import datetime
from icecream import ic
from io import StringIO
import chardet
from collections import Counter
import string
import aiofiles
import asyncio
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential

ENABLE_LOGGING = False
CHUNK_SIZE = 8192
MAX_RETRIES = 3
T = TypeVar('T')
AsyncFunc = Callable[..., AsyncGenerator[Dict[str, Any], None]]

def include_metadata_decorator(field_name: str, value_func: Callable) -> Callable[[AsyncFunc], AsyncFunc]:
    def decorator(func: AsyncFunc) -> AsyncFunc:
        async def wrapper(*args, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
            async for record in func(*args, **kwargs):
                record[field_name] = value_func(args[0])
                yield record
        return wrapper
    return decorator

def include_file_origin(func: AsyncFunc) -> AsyncFunc:
    return include_metadata_decorator("file_origin", lambda x: Path(x).stem)(func)

def include_file_date_created(func: AsyncFunc) -> AsyncFunc:
    return include_metadata_decorator("created_at", lambda x: Path(x).stat().st_ctime)(func)

def include_file_date_imported(func: AsyncFunc) -> AsyncFunc:
    return include_metadata_decorator("imported_at", 
                                    lambda _: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))(func)

@asynccontextmanager
async def managed_file_reader(file_path: Path, encoding: str, **kwargs):
    buffer = StringIO()
    try:
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(kwargs.get('chunk_size', CHUNK_SIZE)):
                cleaned = await process_chunk(chunk, encoding)
                buffer.write(cleaned)
        buffer.seek(0)
        yield buffer
    finally:
        buffer.close()

async def process_chunk(chunk: bytes, encoding: str) -> str:
    return await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: chunk.replace(b'\x00', b'').decode(encoding)
    )

async def process_rows_batch(rows: List[Dict[str, Any]], 
                           uppercase: bool, 
                           lowercase: bool, 
                           state: str | None = None,
                           batch_size: int = 1000) -> List[Dict[str, Any]]:
    tasks = [
        process_record(row, uppercase, lowercase, state)
        for row in rows
    ]
    return await asyncio.gather(*tasks)

@retry(stop=stop_after_attempt(MAX_RETRIES), 
       wait=wait_exponential(multiplier=1, min=4, max=10))
async def detect_encoding(content: bytes) -> str:
    return await asyncio.get_event_loop().run_in_executor(None, chardet.detect, content)

@dataclass
class ReadCSV:
    @classmethod
    @retry(stop=stop_after_attempt(MAX_RETRIES))
    async def detect_file_encoding(cls, file: Path) -> str:
        ic.configureOutput(prefix='detect_file_encoding()|') if ENABLE_LOGGING else ic.disable()
        async with aiofiles.open(file, 'rb') as f:
            content = await f.read(CHUNK_SIZE * 5)
            result = await detect_encoding(content)
            ic(f"Detected encoding: {result['encoding']}") if ENABLE_LOGGING else None
            return result['encoding'] or 'utf-8'

    @classmethod
    async def detect_delimiter(cls, file_path: Path, num_lines: int = 10) -> str:
        common_delimiters = [',', '\t', ';', '|']
        delimiter_counts = {delimiter: 0 for delimiter in common_delimiters}
        
        encoding = await cls.detect_file_encoding(file_path)
        async with managed_file_reader(file_path, encoding) as buffer:
            for _ in range(num_lines):
                line = buffer.readline()
                if not line:
                    break
                counts = Counter(line)
                for delimiter in common_delimiters:
                    delimiter_counts[delimiter] += counts[delimiter]

        detected = max(delimiter_counts, key=delimiter_counts.get)
        ic(f"Detected delimiter: {detected}") if ENABLE_LOGGING else None
        return detected

    @classmethod
    async def clean_and_read_csv(cls, 
                                file_path: Path, 
                                delimiter: str = ',',
                                **csv_kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        encoding = csv_kwargs.get('encoding') or await cls.detect_file_encoding(file_path)
        
        async with managed_file_reader(file_path, encoding, **csv_kwargs) as buffer:
            reader = csv.DictReader(buffer, delimiter=delimiter)
            batch = []
            
            for row in reader:
                batch.append(row)
                if len(batch) >= CHUNK_SIZE:
                    cleaned_rows = await process_rows_batch(batch, **csv_kwargs)
                    for cleaned_row in cleaned_rows:
                        yield cleaned_row
                    batch = []
            
            if batch:
                cleaned_rows = await process_rows_batch(batch, **csv_kwargs)
                for cleaned_row in cleaned_rows:
                    yield cleaned_row

    @classmethod
    @include_file_origin
    @include_file_date_created
    @include_file_date_imported
    async def async_read_csv(cls, 
                      file: Union[str, Path], 
                      **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        file = Path(file) if isinstance(file, str) else file
        
        encoding = kwargs.get("encoding") or await cls.detect_file_encoding(file)
        delimiter = kwargs.get("delimiter") or await cls.detect_delimiter(file)
        
        if file.suffix not in {'.csv', '.txt'}:
            return
            
        async for record in cls.clean_and_read_csv(
            file,
            delimiter=delimiter,
            encoding=encoding,
            **kwargs
        ):
            yield record

async def process_record(record: Dict[str, Any], 
                        uppercase: bool, 
                        lowercase: bool, 
                        state: str | None = None) -> Dict[str, Any]:
    record = {k: (None if isinstance(v, str) and not v.strip() else v) 
             for k, v in record.items()}
    
    if uppercase:
        record = {k.upper(): v for k, v in record.items() if k}
    elif lowercase:
        record = {k.lower(): v for k, v in record.items() if k}
        
    if state:
        record["state"] = state
    
    return record

def read_csv(file: Union[str, Path], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
    return ReadCSV.async_read_csv(file, **kwargs)

async def async_read_batch_csv_files(files: List[Union[str, Path]], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
    async def process_single_file(file: Union[str, Path], **kwargs):
        async for record in ReadCSV.async_read_csv(file, **kwargs):
            yield record
            
    tasks = [asyncio.create_task(process_single_file(file, **kwargs)) for file in files]
    
    for task in asyncio.as_completed(tasks):
        async for record in await task:
            yield record

def read_csv_file_batch(files: List[Union[str, Path]], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
    return asyncio.run(async_read_batch_csv_files(files, **kwargs))