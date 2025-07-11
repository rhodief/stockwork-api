from dataclasses import dataclass, field
from typing import List
from .column_def import ColumnDef

@dataclass
class TableDef:
    name: str
    columns: List[ColumnDef] = field(default_factory=list[ColumnDef])
