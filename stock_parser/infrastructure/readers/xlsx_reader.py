import pandas as pd
from core.models.column_def import ColumnDef
from core.models.table_def import TableDef

def read_schema_from_xlsx(path: str) -> list[TableDef]:
    workbook = pd.read_excel(path, sheet_name=None) # type: ignore
    tables: list[TableDef] = []
    for sheet_name, df in workbook.items():
        columns: list[ColumnDef] = []
        for _, row in df.iterrows(): # type: ignore
            col = ColumnDef(
                name=row["name"], # type: ignore
                type=row["type"], # type: ignore
                required=bool(row.get("required", False)), # type: ignore
                primary_key=bool(row.get("primary_key", False)), # type: ignore
                unique=bool(row.get("unique", False)), # type: ignore
                foreign_key=row.get("foreign_key"), # type: ignore
                default=row.get("default"), # type: ignore
                comment=row.get("comment") # type: ignore
            )
            columns.append(col)
        tables.append(TableDef(name=sheet_name, columns=columns))
    return tables
