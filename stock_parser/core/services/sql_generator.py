from stock_parser.core.models.table_def import TableDef
import re

def validate_identifier(identifier: str, kind: str = "identifier") -> None:
    """
    Validates a SQL identifier (table name, column name).
    Raises ValueError if unsafe.
    """
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid {kind}: '{identifier}'")

def generate_create_sql(table: TableDef) -> tuple[str, list[str]]:
    validate_identifier(table.name, "table name")

    lines = [f"CREATE TABLE {table.name} ("]
    comments: list[str] = []

    for col in table.columns:
        validate_identifier(col.name, "column name")

        col_type = map_type(col.type)
        col_line = f"  {col.name} {col_type}"

        if col.primary_key:
            col_line += " PRIMARY KEY"
        if col.required:
            col_line += " NOT NULL"
        if col.unique:
            col_line += " UNIQUE"
        if col.default is not None:
            col_line += f" DEFAULT {col.default}"
        if col.foreign_key:
            # Expecting format: "referenced_table.referenced_column"
            try:
                ref_table, ref_column = col.foreign_key.split(".")
                validate_identifier(ref_table, "foreign key table")
                validate_identifier(ref_column, "foreign key column")
                col_line += f" REFERENCES {ref_table}({ref_column})"
            except ValueError:
                raise ValueError(f"Invalid foreign key format for column '{col.name}': {col.foreign_key}")

        lines.append(col_line + ",")

        if col.comment:
            sanitized_comment = col.comment.replace("'", "''")
            comments.append(
                f"COMMENT ON COLUMN {table.name}.{col.name} IS '{sanitized_comment}';"
            )

    lines[-1] = lines[-1].rstrip(",")
    lines.append(");")

    return "\n".join(lines), comments

def generate_drop_sql(table: TableDef, if_exists: bool = True, cascade: bool = False) -> str:
    validate_identifier(table.name, "table name")

    sql = f"DROP TABLE {'IF EXISTS ' if if_exists else ''}{table.name}"
    if cascade:
        sql += " CASCADE"
    return sql + ";"

def map_type(logical_type: str) -> str:
    base_types = {
        "text": "TEXT",
        "integer": "INTEGER",
        "float": "DOUBLE PRECISION",
        "boolean": "BOOLEAN",
        "date": "DATE"
    }

    if logical_type in base_types:
        return base_types[logical_type]

    geometry_pattern = re.compile(r'^geometry\(\s*\w+\s*(,\s*\d+)?\s*\)$', re.IGNORECASE)
    if geometry_pattern.match(logical_type):
        return logical_type

    raise ValueError(f"Unsupported or unsafe type: '{logical_type}'")
