import unittest

from src.db.backend.errors import (
    EmptyFieldError,
    EmptyTableError,
    InvalidFieldError,
    InvalidSchemaError,
    InvalidTypeError,
    RecordNotFoundError,
    TableAlreadyExistsError,
    TableNotCreatedError,
    ValidationError,
)
from src.db.backend.memory import Database, Table


class TestTable(unittest.TestCase):
    def setUp(self):
        self.table = Table("students", {"id": "int", "name": "str", "score": "float"})

    def test_validate_valid_values(self):
        self.assertEqual(self.table.validate("id", "10"), 10)
        self.assertEqual(self.table.validate("score", "4.5"), 4.5)
        self.assertEqual(self.table.validate("name", "Иван"), "Иван")

    def test_validate_invalid_field(self):
        with self.assertRaises(InvalidFieldError):
            self.table.validate("age", "10")

    def test_validate_empty_value(self):
        with self.assertRaises(EmptyFieldError):
            self.table.validate("name", "")

        with self.assertRaises(EmptyFieldError):
            self.table.validate("name", None)

    def test_validate_invalid_int_and_float(self):
        with self.assertRaises(InvalidTypeError):
            self.table.validate("id", "abc")

        with self.assertRaises(InvalidTypeError):
            self.table.validate("score", "abc")

    def test_validate_string_cannot_be_only_digits(self):
        with self.assertRaises(InvalidTypeError):
            self.table.validate("name", "123")

    def test_validate_unknown_type_in_schema(self):
        table = Table("bad", {"flag": "bool"})

        with self.assertRaises(InvalidTypeError):
            table.validate("flag", "true")

    def test_insert_valid_record_and_convert_types(self):
        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})

        self.assertEqual(
            self.table.select(),
            [{"id": 1, "name": "Иван", "score": 4.5}],
        )

    def test_insert_missing_field(self):
        with self.assertRaises(ValidationError):
            self.table.insert({"id": "1", "name": "Иван"})

    def test_select_returns_copy(self):
        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})
        selected = self.table.select()
        selected[0]["name"] = "Петр"

        self.assertEqual(self.table.select()[0]["name"], "Иван")

    def test_sort_ascending_and_descending(self):
        self.table.insert({"id": "2", "name": "Петр", "score": "3.0"})
        self.table.insert({"id": "1", "name": "Иван", "score": "5.0"})

        self.assertEqual([row["id"] for row in self.table.sort("id")], [1, 2])
        self.assertEqual(
            [row["id"] for row in self.table.sort("id", asc=False)], [2, 1]
        )

    def test_sort_invalid_field_and_empty_table(self):
        with self.assertRaises(InvalidFieldError):
            self.table.sort("age")

        with self.assertRaises(EmptyTableError):
            self.table.sort("id")

    def test_search_all_and_by_filters(self):
        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})
        self.table.insert({"id": "2", "name": "Мария", "score": "5.0"})

        self.assertEqual(len(self.table.search()), 2)
        self.assertEqual(
            self.table.search({"id": "2"}),
            [{"id": 2, "name": "Мария", "score": 5.0}],
        )

    def test_search_errors(self):
        with self.assertRaises(EmptyTableError):
            self.table.search({"id": "1"})

        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})

        with self.assertRaises(InvalidFieldError):
            self.table.search({"age": "20"})

        with self.assertRaises(RecordNotFoundError):
            self.table.search({"id": "2"})

    def test_update_by_filter_and_value_filter(self):
        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})
        self.table.insert({"id": "2", "name": "Мария", "score": "5.0"})

        self.assertEqual(
            self.table.update(filters={"id": "1"}, updates={"name": "Петр"}),
            1,
        )
        self.assertEqual(self.table.search({"id": "1"})[0]["name"], "Петр")

        self.assertEqual(
            self.table.update(value_filter="Мария", updates={"score": "4.0"}),
            1,
        )
        self.assertEqual(self.table.search({"id": "2"})[0]["score"], 4.0)

    def test_update_errors(self):
        with self.assertRaises(EmptyTableError):
            self.table.update(updates={"name": "Петр"})

        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})

        with self.assertRaises(ValidationError):
            self.table.update(filters={"id": "1"}, updates=None)

        with self.assertRaises(InvalidFieldError):
            self.table.update(filters={"age": "20"}, updates={"name": "Петр"})

        with self.assertRaises(InvalidFieldError):
            self.table.update(filters={"id": "1"}, updates={"age": "20"})

        with self.assertRaises(RecordNotFoundError):
            self.table.update(filters={"id": "2"}, updates={"name": "Петр"})

        with self.assertRaises(RecordNotFoundError):
            self.table.update(value_filter="нет такого", updates={"name": "Петр"})

    def test_delete_all_by_filter_and_by_value_filter(self):
        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})
        self.table.insert({"id": "2", "name": "Мария", "score": "5.0"})
        self.table.insert({"id": "3", "name": "Петр", "score": "3.0"})

        self.assertEqual(self.table.delete(filters={"id": "1"}), 1)
        self.assertEqual(self.table.delete(value_filter="Мария"), 1)
        self.assertEqual(self.table.delete(), 1)
        self.assertEqual(self.table.select(), [])

    def test_delete_errors(self):
        with self.assertRaises(EmptyTableError):
            self.table.delete()

        self.table.insert({"id": "1", "name": "Иван", "score": "4.5"})

        with self.assertRaises(InvalidFieldError):
            self.table.delete(filters={"age": "20"})

        with self.assertRaises(RecordNotFoundError):
            self.table.delete(filters={"id": "2"})

        with self.assertRaises(RecordNotFoundError):
            self.table.delete(value_filter="нет такого")


class TestDatabase(unittest.TestCase):
    def test_create_table_and_get_table(self):
        db = Database()
        db.create_table(" students ", {" id ": "int", " name ": "str"})

        self.assertEqual(db.get_current_name(), "students")
        self.assertEqual(db.get_table().name, "students")
        self.assertEqual(db.get_table().schema, {"id": "int", "name": "str"})
        self.assertEqual(db.list_tables(), ["students"])

    def test_create_table_errors(self):
        db = Database()

        with self.assertRaises(EmptyFieldError):
            db.create_table("", {"id": "int"})

        with self.assertRaises(InvalidSchemaError):
            db.create_table("students", {"": "int"})

        with self.assertRaises(InvalidTypeError):
            db.create_table("students", {"id": "integer"})

        db.create_table("students", {"id": "int"})

        with self.assertRaises(TableAlreadyExistsError):
            db.create_table("students", {"id": "int"})

    def test_switch_table(self):
        db = Database()
        db.create_table("students", {"id": "int"})
        db.create_table("teachers", {"id": "int"})
        db.switch_table(" students ")

        self.assertEqual(db.get_current_name(), "students")

    def test_database_errors_without_tables(self):
        db = Database()

        self.assertEqual(db.get_current_name(), "не выбрана")

        with self.assertRaises(TableNotCreatedError):
            db.get_table()

        with self.assertRaises(TableNotCreatedError):
            db.list_tables()

        with self.assertRaises(TableNotCreatedError):
            db.switch_table("students")

    def test_save_methods_do_nothing_for_memory_database(self):
        db = Database()
        self.assertIsNone(db.save_current())
        self.assertIsNone(db.save_all())


if __name__ == "__main__":
    unittest.main()
