import json
import tempfile
import unittest
from pathlib import Path

from src.db.backend.errors import (
    InvalidSchemaError,
    InvalidStorageDataError,
    InvalidTypeError,
    TableNotCreatedError,
)
from src.db.backend.file_json import JsonFileDatabase


class TestJsonFileDatabase(unittest.TestCase):
    def test_create_table_saves_json_file(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JsonFileDatabase(directory)
            db.create_table("students", {"id": "int", "name": "str"})

            path = Path(directory) / "students.json"
            self.assertTrue(path.exists())

            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], "students")
            self.assertEqual(data["schema"], {"id": "int", "name": "str"})
            self.assertEqual(data["records"], [])

    def test_data_is_saved_between_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            first_db = JsonFileDatabase(directory)
            first_db.create_table(
                "students", {"id": "int", "name": "str", "score": "float"}
            )
            first_db.get_table().insert({"id": "1", "name": "Иван", "score": "4.5"})
            first_db.save_current()

            second_db = JsonFileDatabase(directory)
            second_db.switch_table("students")

            self.assertEqual(
                second_db.get_table().select(),
                [{"id": 1, "name": "Иван", "score": 4.5}],
            )

    def test_update_delete_and_save_all_are_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JsonFileDatabase(directory)
            db.create_table("students", {"id": "int", "name": "str"})
            db.get_table().insert({"id": "1", "name": "Иван"})
            db.get_table().insert({"id": "2", "name": "Мария"})
            db.save_current()

            db.get_table().update(filters={"id": "1"}, updates={"name": "Петр"})
            db.get_table().delete(filters={"id": "2"})
            db.save_all()

            loaded_db = JsonFileDatabase(directory)
            loaded_db.switch_table("students")

            self.assertEqual(
                loaded_db.get_table().select(),
                [{"id": 1, "name": "Петр"}],
            )

    def test_multiple_tables_are_loaded_and_current_is_set(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JsonFileDatabase(directory)
            db.create_table("students", {"id": "int"})
            db.create_table("teachers", {"id": "int"})
            db.save_all()

            loaded = JsonFileDatabase(directory)

            self.assertEqual(set(loaded.list_tables()), {"students", "teachers"})
            self.assertIn(loaded.get_current_name(), {"students", "teachers"})

    def test_invalid_table_name_with_path_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JsonFileDatabase(directory)

            with self.assertRaises(InvalidSchemaError):
                db.create_table("bad/name", {"id": "int"})

            with self.assertRaises(InvalidSchemaError):
                db._get_table_path("bad\\name")

    def test_save_current_without_current_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JsonFileDatabase(directory)

            with self.assertRaises(TableNotCreatedError):
                db.save_current()

    def test_save_unknown_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JsonFileDatabase(directory)

            with self.assertRaises(TableNotCreatedError):
                db._save_table("missing")

    def test_load_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text("{bad json", encoding="utf-8")

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_json_not_object(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text("[]", encoding="utf-8")

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_invalid_name(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps({"name": "", "schema": {"id": "int"}, "records": []}),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_invalid_schema_type(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps({"name": "bad", "schema": [], "records": []}),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_records_must_be_list(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps({"name": "bad", "schema": {"id": "int"}, "records": {}}),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_record_must_be_dict(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps({"name": "bad", "schema": {"id": "int"}, "records": [1]}),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_record_must_match_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps(
                    {
                        "name": "bad",
                        "schema": {"id": "int", "name": "str"},
                        "records": [{"id": "abc", "name": "Иван"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_schema_field_name_must_be_string(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps({"name": "bad", "schema": {"": "int"}, "records": []}),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidStorageDataError):
                JsonFileDatabase(directory)

    def test_load_schema_type_must_be_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "bad.json").write_text(
                json.dumps({"name": "bad", "schema": {"id": "integer"}, "records": []}),
                encoding="utf-8",
            )

            with self.assertRaises(InvalidTypeError):
                JsonFileDatabase(directory)


if __name__ == "__main__":
    unittest.main()
