from typing import Dict, List

TABLES: Dict[str, List[dict]] = {}
SCHEMAS: Dict[str, Dict[str, type]] = {}

CURRENT_TABLE: str | None = None

def create_table(name: str, schema: Dict[str, type]) -> None:
    if name in TABLES:
        raise ValueError("Таблица уже существует")

    TABLES[name] = []
    SCHEMAS[name] = schema


def use_table(name: str) -> None:
    global CURRENT_TABLE

    if name not in TABLES:
        raise ValueError("Таблица не найдена")

    CURRENT_TABLE = name


def get_current_table() -> str:
    if CURRENT_TABLE is None:
        raise ValueError("Текущая таблица не выбрана")

    return CURRENT_TABLE


def list_tables():
    return {
        name: {
            "schema": SCHEMAS[name],
            "count": len(TABLES[name])
        }
        for name in TABLES
    }

def create_record(table: str, **data):
    schema = SCHEMAS[table]

    record = {}

    for field, expected_type in schema.items():

        if field not in data:
            raise ValueError(f"Нет поля {field}")

        value = data[field]

        if not isinstance(value, expected_type):
            raise ValueError(
                f"Поле {field} должно быть типа {expected_type.__name__}"
            )

        record[field] = value

    TABLES[table].append(record)

    return record


def select_record(table: str, **filters):
    rows = TABLES[table]

    if not filters:
        return rows.copy()

    result = []

    for row in rows:

        ok = True

        for key, value in filters.items():

            if row.get(key) != value:
                ok = False
                break

        if ok:
            result.append(row)

    return result


def update_record(table: str, filters: dict, updates: dict):
    rows = TABLES[table]

    updated = 0

    for row in rows:

        ok = True

        for key, value in filters.items():

            if row.get(key) != value:
                ok = False
                break

        if ok:
            row.update(updates)
            updated += 1

    return updated


def delete_record(table: str, **filters):
    rows = TABLES[table]

    if not filters:
        deleted = len(rows)
        rows.clear()
        return deleted

    new_rows = []
    deleted = 0

    for row in rows:

        ok = True

        for key, value in filters.items():

            if row.get(key) != value:
                ok = False
                break

        if ok:
            deleted += 1
        else:
            new_rows.append(row)

    TABLES[table] = new_rows

    return deleted