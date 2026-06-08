import csv
import tempfile
import unittest
from pathlib import Path

from src.db.backend.errors import (
    InvalidSchemaError,
    InvalidStorageDataError,
    InvalidTypeError,
    TableNotCreatedError,
)
from src.db.backend.file_csv import CsvFileDatabase


class TestCsvFileDatabase(unittest.TestCase):
    def write_csv(self, directory, filename, rows):
        path = Path(directory) / filename
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        return path

    def test_create_table_saves_csv_file(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvFileDatabase(directory)
            db.create_table("students", {"id": "int", "name": "str"})

            path = Path(directory) / "students.csv"
            self.assertTrue(path.exists())
            self.assertEqual(
                path.read_text(encoding="utf-8").splitlines()[:2],
                ["__schema__,id:int,name:str", "id,name"],
            )

    def test_data_is_saved_between_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            first_db = CsvFileDatabase(directory)
            first_db.create_table(
                "students", {"id": "int", "name": "str", "score": "float"}
            )
            first_db.get_table().insert({"id": "1", "name": "Мария", "score": "5.0"})
            first_db.save_current()

            second_db = CsvFileDatabase(directory)
            second_db.switch_table("students")

            self.assertEqual(
                second_db.get_table().select(),
                [{"id": 1, "name": "Мария", "score": 5.0}],
            )

    def test_update_delete_and_save_all_are_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvFileDatabase(directory)
            db.create_table("students", {"id": "int", "name": "str"})
            db.get_table().insert({"id": "1", "name": "Иван"})
            db.get_table().insert({"id": "2", "name": "Мария"})
            db.save_current()

            db.get_table().update(filters={"id": "1"}, updates={"name": "Петр"})
            db.get_table().delete(filters={"id": "2"})
            db.save_all()

            loaded_db = CsvFileDatabase(directory)
            loaded_db.switch_table("students")

            self.assertEqual(
                loaded_db.get_table().select(),
                [{"id": 1, "name": "Петр"}],
            )

    def test_multiple_tables_are_loaded_and_current_is_set(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvFileDatabase(directory)
            db.create_table("students", {"id": "int"})
            db.create_table("teachers", {"id": "int"})
            db.save_all()

            loaded = CsvFileDatabase(directory)

            self.assertEqual(set(loaded.list_tables()), {"students", "teachers"})
            self.assertIn(loaded.get_current_name(), {"students", "teachers"})

    def test_invalid_table_name_with_path_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvFileDatabase(directory)

            with self.assertRaises(InvalidSchemaError):
                db.create_table("bad/name", {"id": "int"})

            with self.assertRaises(InvalidSchemaError):
                db._get_table_path("bad\\name")

    def test_save_current_without_current_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvFileDatabase(directory)

            with self.assertRaises(TableNotCreatedError):
                db.save_current()

    def test_save_unknown_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = CsvFileDatabase(directory)

            with self.assertRaises(TableNotCreatedError):
                db._save_table("missing")

    def test_load_incomplete_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(directory, "bad.csv", [["__schema__", "id:int"]])

            with self.assertRaises(InvalidStorageDataError):
                CsvFileDatabase(directory)

    def test_load_missing_schema_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(directory, "bad.csv", [["schema", "id:int"], ["id"]])

            with self.assertRaises(InvalidStorageDataError):
                CsvFileDatabase(directory)

    def test_load_header_must_match_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(directory, "bad.csv", [["__schema__", "id:int"], ["name"]])

            with self.assertRaises(InvalidStorageDataError):
                CsvFileDatabase(directory)

    def test_load_schema_cell_must_have_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(directory, "bad.csv", [["__schema__", "id-int"], ["id"]])

            with self.assertRaises(InvalidStorageDataError):
                CsvFileDatabase(directory)

    def test_load_schema_type_must_be_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(directory, "bad.csv", [["__schema__", "id:integer"], ["id"]])

            with self.assertRaises(InvalidTypeError):
                CsvFileDatabase(directory)

    def test_load_row_must_have_valid_number_of_values(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(
                directory,
                "bad.csv",
                [["__schema__", "id:int", "name:str"], ["id", "name"], ["1"]],
            )

            with self.assertRaises(InvalidStorageDataError):
                CsvFileDatabase(directory)

    def test_load_record_must_match_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_csv(
                directory,
                "bad.csv",
                [["__schema__", "id:int", "name:str"], ["id", "name"], ["abc", "Иван"]],
            )

            with self.assertRaises(InvalidStorageDataError):
                CsvFileDatabase(directory)


if __name__ == "__main__":
    unittest.main()
