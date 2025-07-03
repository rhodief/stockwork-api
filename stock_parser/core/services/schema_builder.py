import json
from stock_parser.core.models.table_def import TableDef
from stock_parser.core.models.column_def import ColumnDef

def build_from_json(json_path: str) -> list[TableDef]:
    with open(json_path, "r") as f:
        data = json.load(f)
    tables: list[TableDef] = []
    for table in data:
        columns = [ColumnDef(**col) for col in table["columns"]]
        tables.append(TableDef(name=table["table_name"], columns=columns))
    return tables
