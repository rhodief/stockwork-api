from collections import defaultdict, deque
from typing import Optional
from stock_parser.core.models.table_def import TableDef



def sort_tables_by_dependency(
    tables: list[TableDef],
    ignore_missing_refs: Optional[list[str]] = None
) -> list[TableDef]:
    """
    Ordena tabelas com base nas dependências entre chaves estrangeiras.

    Parâmetros:
        tables: Lista de definições de tabela.
        ignore_missing_refs: Lista de chaves estrangeiras a ignorar (ex: "spatial_ref_sys.srid").

    Retorna:
        Lista ordenada de TableDef respeitando as dependências.

    Exceções:
        ValueError: Se houver:
            - Referência inválida de FK (formato);
            - Referência a tabela ausente (exceto ignoradas);
            - Ciclo real de dependência.
    """
    ignored_list: list[str] = ignore_missing_refs if ignore_missing_refs is not None else []
    ignore_missing_set: set[str] = set(ignored_list)
    name_to_table: dict[str, TableDef] = {table.name: table for table in tables}
    existing_tables = set(name_to_table.keys())
    graph: dict[str, set[str]] = defaultdict(set)
    reverse_graph: dict[str, set[str]] = defaultdict(set)
    missing_refs: dict[str, set[str]] = defaultdict(set)

    for table in tables:
        for col in table.columns:
            if col.foreign_key:
                try:
                    ref_table, ref_column = col.foreign_key.split(".")
                except ValueError:
                    raise ValueError(
                        f"Invalid foreign_key format in {table.name}.{col.name}: {col.foreign_key}"
                    )
                fk_full = f"{ref_table}.{ref_column}"
                if ref_table not in existing_tables:
                    if fk_full not in ignore_missing_set:
                        missing_refs[table.name].add(ref_table)
                else:
                    graph[table.name].add(ref_table)
                    reverse_graph[ref_table].add(table.name)

    if missing_refs:
        msg = "Missing table references detected:\n"
        msg += "\n".join(
            f"- {table} references missing table(s): {sorted(refs)}"
            for table, refs in missing_refs.items()
        )
        raise ValueError(msg)

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
                del graph[dependent_name]

    if len(sorted_tables) != len(tables):
        unresolved = {k: v for k, v in graph.items() if v}
        cycle_info = "\n".join(f"- {k} depends on {sorted(v)}" for k, v in unresolved.items())
        raise ValueError(f"Cyclic dependency detected among tables:\n{cycle_info}")

    return sorted_tables