from dataclasses import dataclass
from typing import Optional

@dataclass
class ColumnDef:
    name: str
    type: str
    primary_key: bool = False
    required: bool = False
    unique: bool = False
    foreign_key: Optional[str] = None
    default: Optional[str] = None
    comment: Optional[str] = None
