from stock_parser.core.services import create_tables_from_json, drop_tables_from_json
from stock_parser.infrastructure.connectors.sqlalchemy_connector import SQLAlchemyConnector
import os

connector = SQLAlchemyConnector(db_url=os.environ.get('DATABASE_URL', ''))

def create_tables():
    create_tables_from_json("stock_parser/config/base_model.json", connector)

def drop_tables():
    drop_tables_from_json("stock_parser/config/base_model.json", connector)

if __name__ == '__main__':
    drop_tables()
    #create_tables()    
    
    