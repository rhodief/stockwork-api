from stock_parser.core.services.schema_analyzer import sort_tables_by_dependency
from stock_parser.core.services.schema_builder import build_from_json
from stock_parser.infrastructure.connectors.sqlalchemy_connector import SQLAlchemyConnector
import os

connector = SQLAlchemyConnector(db_url=os.environ.get('DATABASE_URL', ''))
tables = build_from_json("stock_parser/config/base_model.json")
sorted_tables = sort_tables_by_dependency(tables, ignore_missing_refs=['spatial_ref_sys.srid'])
for table in sorted_tables:
    connector.create_table(table)
    #connector.drop_table(table)