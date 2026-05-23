import unittest

from src.db.backend.memory import Table, Database
from src.db.backend.errors import (
    TableNotCreatedError,
    TableAlreadyExistsError,
    EmptyTableError,
    EmptyFieldError,
    InvalidFieldError,
    InvalidTypeError,
    ValidationError,
    InvalidSchemaError,
    RecordNotFoundError,
)


class TestTable(unittest.TestCase):

    def setUp(self):
        self.table = Table(
            "students",
            {
                "id": "int",
                "name": "str",
                "score": "float",
            },
        )

        self.assertIsInstance(self.table, Table)

    def test_validate_success(self):

        cases = [
            ("id", "1", 1),
            ("id", 5, 5),
            ("score", "4.5", 4.5),
            ("name", "John", "John"),
        ]

        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                result = self.table.validate(field, value)
                self.assertEqual(result, expected)

    def test_validate_invalid_field(self):

        with self.assertRaises(InvalidFieldError):
            self.table.validate("age", 10)

    def test_validate_empty(self):

        cases = [
            ("id", ""),
            ("name", None),
        ]

        for field, value in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(EmptyFieldError):
                    self.table.validate(field, value)

    def test_validate_invalid_type(self):

        cases = [
            ("id", "abc"),
            ("score", "text"),
        ]

        for field, value in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(InvalidTypeError):
                    self.table.validate(field, value)

    def test_validate_str_digits_only(self):

        with self.assertRaises(InvalidTypeError):
            self.table.validate("name", "12345")

    def test_insert_success(self):

        record = {
            "id": "1",
            "name": "Alice",
            "score": "5.5",
        }

        self.table.insert(record)

        self.assertEqual(len(self.table.rows), 1)

        self.assertEqual(
            self.table.rows[0],
            {
                "id": 1,
                "name": "Alice",
                "score": 5.5,
            },
        )

    def test_insert_missing_field(self):

        record = {
            "id": 1,
            "name": "Bob",
        }

        with self.assertRaises(ValidationError):
            self.table.insert(record)

    def test_select(self):

        self.table.insert(
            {
                "id": 1,
                "name": "Tom",
                "score": 4.0,
            }
        )

        records = self.table.select()

        self.assertEqual(len(records), 1)

    def test_sort_asc(self):

        self.table.insert({"id": 2, "name": "B", "score": 8.0})
        self.table.insert({"id": 1, "name": "A", "score": 5.0})

        result = self.table.sort("id")

        self.assertEqual(result[0]["id"], 1)

    def test_sort_desc(self):

        self.table.insert({"id": 2, "name": "B", "score": 8.0})
        self.table.insert({"id": 1, "name": "A", "score": 5.0})

        result = self.table.sort("id", asc=False)

        self.assertEqual(result[0]["id"], 2)

    def test_sort_empty(self):

        with self.assertRaises(EmptyTableError):
            self.table.sort("id")

    def test_sort_invalid_field(self):

        with self.assertRaises(InvalidFieldError):
            self.table.sort("age")

    def test_search_without_filters(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})

        result = self.table.search()

        self.assertEqual(len(result), 1)

    def test_search_by_filter(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 7.0})

        result = self.table.search({"id": 2})

        self.assertEqual(result[0]["name"], "Bob")

    def test_search_not_found(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})

        with self.assertRaises(RecordNotFoundError):
            self.table.search({"id": 999})

    def test_search_invalid_field(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})

        with self.assertRaises(InvalidFieldError):
            self.table.search({"age": 10})

    def test_update_by_field(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 7.0})

        updated = self.table.update(
            filters={"id": 1},
            updates={"name": "Alex"},
        )

        self.assertEqual(updated, 1)
        self.assertEqual(self.table.rows[0]["name"], "Alex")

    def test_update_by_value(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 5.0})

        updated = self.table.update(
            value_filter="5.0",
            updates={"name": "Updated"},
        )

        self.assertEqual(updated, 2)

    def test_update_by_field_and_value(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 5.0})

        updated = self.table.update(
            filters={"id": 1},
            value_filter="5.0",
            updates={"name": "One"},
        )

        self.assertEqual(updated, 1)

    def test_update_without_updates(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})

        with self.assertRaises(ValidationError):
            self.table.update(filters={"id": 1})

    def test_update_not_found(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})

        with self.assertRaises(RecordNotFoundError):
            self.table.update(
                filters={"id": 999},
                updates={"name": "X"},
            )

    def test_delete_all(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 7.0})

        deleted = self.table.delete()

        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.table.rows), 0)

    def test_delete_by_field(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 7.0})

        deleted = self.table.delete(filters={"id": 1})

        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.table.rows), 1)

    def test_delete_by_value(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})
        self.table.insert({"id": 2, "name": "Bob", "score": 5.0})

        deleted = self.table.delete(value_filter="5.0")

        self.assertEqual(deleted, 2)

    def test_delete_not_found(self):

        self.table.insert({"id": 1, "name": "Tom", "score": 5.0})

        with self.assertRaises(RecordNotFoundError):
            self.table.delete(filters={"id": 999})


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database()

        self.assertIsInstance(self.db, Database)

    def test_create_table(self):

        schema = {
            "id": "int",
            "name": "str",
        }

        self.db.create_table("users", schema)

        self.assertIn("users", self.db.tables)

    def test_create_table_duplicate(self):

        schema = {
            "id": "int",
        }

        self.db.create_table("users", schema)

        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("users", schema)

    def test_create_table_empty_name(self):

        with self.assertRaises(EmptyFieldError):
            self.db.create_table("", {"id": "int"})

    def test_create_table_invalid_schema(self):

        with self.assertRaises(InvalidSchemaError):
            self.db.create_table("users", {"": "int"})

    def test_create_table_invalid_type(self):

        with self.assertRaises(InvalidTypeError):
            self.db.create_table("users", {"id": "bool"})

    def test_switch_table(self):

        self.db.create_table("users", {"id": "int"})

        self.db.switch_table("users")

        self.assertEqual(self.db.current, "users")

    def test_switch_table_not_found(self):

        with self.assertRaises(TableNotCreatedError):
            self.db.switch_table("missing")

    def test_get_current_name(self):

        self.assertEqual(
            self.db.get_current_name(),
            "не выбрана",
        )

    def test_get_table(self):

        self.db.create_table("users", {"id": "int"})

        table = self.db.get_table()

        self.assertIsInstance(table, Table)

    def test_get_table_not_created(self):

        with self.assertRaises(TableNotCreatedError):
            self.db.get_table()

    def test_list_tables(self):

        self.db.create_table("users", {"id": "int"})

        tables = self.db.list_tables()

        self.assertEqual(tables, ["users"])

    def test_list_tables_empty(self):

        with self.assertRaises(TableNotCreatedError):
            self.db.list_tables()
