from collections import defaultdict, deque
from stock_parser.core.models.table_def import TableDef



def sort_tables_by_dependency(tables: list[TableDef]) -> list[TableDef]:
    """
    Topologically sorts a list of tables based on their foreign key dependencies.

    Args:
        tables: List of TableDef objects.

    Returns:
        A list of TableDef objects sorted in an order that respects FK dependencies.

    Raises:
        ValueError: If cyclic dependencies are detected or FK formats are invalid.
    """
    name_to_table: dict[str, TableDef] = {table.name: table for table in tables}
    graph: dict[str, set[str]] = defaultdict(set)           # table → tables it depends on
    reverse_graph: dict[str, set[str]] = defaultdict(set)   # table → tables that depend on it

    for table in tables:
        for col in table.columns:
            if col.foreign_key:
                try:
                    ref_table, _ = col.foreign_key.split(".")
                    graph[table.name].add(ref_table)
                    reverse_graph[ref_table].add(table.name)
                except ValueError:
                    raise ValueError(
                        f"Invalid foreign_key format in {table.name}.{col.name}: {col.foreign_key}"
                    )

    sorted_tables: list[TableDef] = []
    ready: deque[TableDef] = deque(
        [t for t in tables if not graph.get(t.name)]
    )

    while ready:
        table = ready.popleft()
        sorted_tables.append(table)
        for dependent_name in reverse_graph.get(table.name, set()):
            graph[dependent_name].remove(table.name)
            if not graph[dependent_name]:
                ready.append(name_to_table[dependent_name])

    if len(sorted_tables) != len(tables):
        raise ValueError("Cyclic dependency detected among tables")

    return sorted_tables
