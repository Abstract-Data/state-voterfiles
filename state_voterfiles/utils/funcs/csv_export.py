from __future__ import annotations
import csv
import asyncio
import aiofiles
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Iterable
from pydantic import BaseModel

# from state_voterfiles.utils.logger import Logger


@dataclass
class CSVExport:
    data: Iterable[Dict[str, Any]]
    name: str
    path: Path | str = None
    _file_loc: Path = None

    @property
    def logger(self):
        # return Logger(module_name="CSVExport")
        return None

    @property
    def filename(self) -> str:
        return f'{datetime.now().strftime("%Y%m%d")}_{self.name}.csv'

    @property
    def file_loc(self) -> Path:
        if not self.path:
            self._file_loc = Path(__file__).parents[2] / "data" / "exports" / self.filename
        else:
            self._file_loc = self.path if isinstance(self.path, Path) else Path(self.path)
        return self._file_loc

    async def async_export(self, _path: Path = None) -> 'CSVExport':
        if _path is None:
            raise ValueError("Path is required")
        async with aiofiles.open(_path / self.filename, "w") as f:
            writer = None
            for record in self.data:
                _record = {
                    k: v for k, v in (
                        dict(record) if isinstance(record, BaseModel) else record).items() if k is not None
                }
                if writer is None:
                    writer = csv.DictWriter(f, fieldnames=_record.keys())
                    await f.write(','.join(writer.fieldnames) + '\n')
                # Convert all values to string, handling None values as empty strings
                cleaned_record = {k: (str(v) if v is not None else '') for k, v in record.items()}
                await f.write(','.join(cleaned_record[key] for key in writer.fieldnames) + '\n')
                # await f.write(','.join(str(_record.get(key, '')) for key in writer.fieldnames) + '\n')
        # self.logger.info(f"Exported {self.filename} to {_path.name}")
        return self

    def export(self, path: Path = Path(__file__).parents[2] / "data" / "exports") -> 'CSVExport':
        _path = path if not self.path else self.path
        asyncio.run(self.async_export(_path))
        return self