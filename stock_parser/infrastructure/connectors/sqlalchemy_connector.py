from sqlalchemy import create_engine, text
from stock_parser.core.ports.database_interface import DatabaseInterface
from stock_parser.core.services.sql_generator import generate_create_sql, generate_drop_sql
from stock_parser.core.models.table_def import TableDef

class SQLAlchemyConnector(DatabaseInterface):
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def execute(self, sql: str):
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def create_table(self, table: TableDef):
        create_sql, comments = generate_create_sql(table)
        self.execute(create_sql)
        for comment_sql in comments:
            self.execute(comment_sql)
            
    def drop_table(self, table: TableDef):
        drop_sql = generate_drop_sql(table, cascade=True)
        self.execute(drop_sql)
            
