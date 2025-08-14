# Stockwork

## Application Design

### Main Modules:
- **Projects:** setup each project with its own schema and futher definitions
    - *view*: project details. Each aspect of the project in tabs. Here we can submit data sheets. 
    - *config*: All stuff for projects configs. 
- **Data Sheets:** Pages for the last datasheets submited and its validations and flags for pipeline ready (see if it's need)
- **Sites mapping:** The map and relevant data to see it in the map across all projects. It must also stay in the projet tab for "mapping". 
- **Configs:** App configuration as a whole. 


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
