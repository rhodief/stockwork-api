import pandas as pd
from core.models.column_def import ColumnDef
from core.models.table_def import TableDef

def read_schema_from_xlsx(path: str) -> list[TableDef]:
    workbook = pd.read_excel(path, sheet_name=None)
    tables = []
    for sheet_name, df in workbook.items():
        columns = []
        for _, row in df.iterrows():
            col = ColumnDef(
                name=row["name"],
                type=row["type"],
                required=bool(row.get("required", False)),
                primary_key=bool(row.get("primary_key", False)),
                unique=bool(row.get("unique", False)),
                foreign_key=row.get("foreign_key"),
                default=row.get("default"),
                comment=row.get("comment")
            )
            columns.append(col)
        tables.append(TableDef(name=sheet_name, columns=columns))
    return tables
