# Stockwork

# Usage Example

1. JSON-based Table Generation

```python
from core.services.schema_builder import build_from_json
from infrastructure.connectors.sqlalchemy_connector import SQLAlchemyConnector

connector = SQLAlchemyConnector(db_url="postgresql://user:pass@localhost/db")
tables = build_from_json("config/base_model.json")
for table in tables:
    connector.create_table(table)
```

2. XLSX-based Table Generation
------------------------------
```python
from infrastructure.readers.xlsx_reader import read_schema_from_xlsx
tables = read_schema_from_xlsx("your_file.xlsx")
# Same logic applies to create tables as above
```
