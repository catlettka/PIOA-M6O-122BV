import pytest
from src.db.backend.memory import Table, Database
from src.db.backend.errors import (
    EmptyTableError,
    InvalidFieldError,
    ValidationError,
    TableAlreadyExistsError,
    TableNotCreatedError,
)

def make_table():
    return Table("users", {"id": "int", "name": "str"})

def test_insert_and_select():
    t = make_table()

    t.insert({"id": 1, "name": "A"})
    t.insert({"id": 2, "name": "B"})

    assert t.select() == [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]

def test_select_empty():
    t = make_table()

    with pytest.raises(EmptyTableError):
        t.select()

def test_sort():
    t = make_table()

    t.insert({"id": 2, "name": "B"})
    t.insert({"id": 1, "name": "A"})

    result = t.sort("id", asc=True)

    assert result[0]["id"] == 1

def test_sort_invalid_field():
    t = make_table()

    with pytest.raises(InvalidFieldError):
        t.sort("unknown")

def test_search_all():
    t = make_table()

    t.insert({"id": 1, "name": "A"})

    assert t.search() == [{"id": 1, "name": "A"}]

def test_search_filter():
    t = make_table()

    t.insert({"id": 1, "name": "A"})
    t.insert({"id": 2, "name": "B"})

    result = t.search({"id": "1"})

    assert result == [{"id": 1, "name": "A"}]

def test_search_empty_error():
    t = make_table()

    with pytest.raises(EmptyTableError):
        t.search({"id": "1"})

def test_update():
    t = make_table()

    t.insert({"id": 1, "name": "A"})

    count = t.update({"id": "1"}, {"name": "NEW"})

    assert count == 1
    assert t.rows[0]["name"] == "NEW"

def test_update_invalid_field():
    t = make_table()

    t.insert({"id": 1, "name": "A"})

    with pytest.raises(InvalidFieldError):
        t.update({"id": "1"}, {"age": 10})

def test_update_not_found():
    t = make_table()

    t.insert({"id": 1, "name": "A"})

    with pytest.raises(ValidationError):
        t.update({"id": "999"}, {"name": "X"})

def test_delete_all():
    t = make_table()

    t.insert({"id": 1})
    t.insert({"id": 2})

    removed = t.delete({})

    assert removed == 2
    assert t.rows == []

def test_delete_filter():
    t = make_table()

    t.insert({"id": 1})
    t.insert({"id": 2})

    removed = t.delete({"id": "1"})

    assert removed == 1
    assert len(t.rows) == 1

def test_delete_not_found():
    t = make_table()

    t.insert({"id": 1})

    with pytest.raises(ValidationError):
        t.delete({"id": "999"})

def test_create_table():
    db = Database()

    db.create_table("users", {"id": "int"})

    assert "users" in db.tables
    assert db.get_current_name() == "users"

def test_duplicate_table():
    db = Database()

    db.create_table("users", {"id": "int"})

    with pytest.raises(TableAlreadyExistsError):
        db.create_table("users", {"id": "int"})

def test_switch_table():
    db = Database()

    db.create_table("users", {"id": "int"})
    db.create_table("posts", {"id": "int"})

    db.switch_table("users")

    assert db.get_current_name() == "users"

def test_switch_invalid():
    db = Database()

    with pytest.raises(TableNotCreatedError):
        db.switch_table("no_table")

def test_get_table():
    db = Database()

    db.create_table("users", {"id": "int"})

    table = db.get_table()

    assert isinstance(table, Table)

def test_list_tables():
    db = Database()

    db.create_table("users", {})
    db.create_table("posts", {})

    tables = db.list_tables()

    assert "users" in tables
    assert "posts" in tables

def test_list_tables_empty():
    db = Database()

    with pytest.raises(TableNotCreatedError):
        db.list_tables()