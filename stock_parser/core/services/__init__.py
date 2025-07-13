

from stock_parser.core.ports.database_interface import DatabaseInterface
from stock_parser.core.services.schema_analyzer import sort_tables_by_dependency
from stock_parser.core.services.schema_builder import build_from_json


def create_tables_from_json(json_path: str, database_connector: DatabaseInterface):
    tables = build_from_json(json_path)
    sorted_tables = sort_tables_by_dependency(tables, ignore_missing_refs=['spatial_ref_sys.srid'])
    for table in sorted_tables:
        database_connector.create_table(table)
        #database_connector.drop_table(table)
    print(f'{len(sorted_tables)} tables have been created')

def drop_tables_from_json(json_path: str, database_connector: DatabaseInterface):
    tables = build_from_json(json_path)
    sorted_tables = sort_tables_by_dependency(tables, ignore_missing_refs=['spatial_ref_sys.srid'])
    for table in sorted_tables:
        database_connector.drop_table(table)
    print(f'{len(sorted_tables)} tables have been dropped')
    

    
