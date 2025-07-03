from abc import ABC, abstractmethod

from stock_parser.core.models.table_def import TableDef

class DatabaseInterface(ABC):
    
    @abstractmethod
    def execute(self, sql: str) -> None: pass

    @abstractmethod
    def create_table(self, table: TableDef) -> None:
        pass
    
    @abstractmethod
    def drop_table(self, table: TableDef) -> None:
        ...