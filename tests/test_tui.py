import unittest
from unittest.mock import patch
from io import StringIO

from src.db.tui import TUI


class TestTUI(unittest.TestCase):

    def setUp(self):
        self.tui = TUI()

    def test_create_table(self):

        inputs = [
            "1",  # меню
            "students",  # имя таблицы
            "3",  # количество полей
            "id",
            "int",
            "name",
            "str",
            "age",
            "int",
            "0",  # выход
        ]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Создано.", output)
                self.assertIn("students", self.tui.db.tables)

    def test_insert_record(self):

        self.tui.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

        inputs = ["2", "1", "Alex", "20", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Запись добавлена.", output)

                rows = self.tui.db.get_table().rows

                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["name"], "Alex")

    def test_show_records(self):

        self.tui.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

        self.tui.db.get_table().insert({"id": 1, "name": "Alex", "age": 20})

        inputs = ["3", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Alex", output)

    def test_update_record(self):

        self.tui.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

        table = self.tui.db.get_table()

        table.insert({"id": 1, "name": "Alex", "age": 20})

        inputs = ["4", "id", "1", "", "name", "Max", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Обновлено:", output)
                self.assertEqual(table.rows[0]["name"], "Max")

    def test_delete_record(self):

        self.tui.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

        table = self.tui.db.get_table()

        table.insert({"id": 1, "name": "Alex", "age": 20})

        inputs = ["5", "id", "1", "", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Удалено:", output)
                self.assertEqual(len(table.rows), 0)

    def test_list_tables(self):

        self.tui.db.create_table("students", {"id": "int"})

        inputs = ["6", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("students", output)

    def test_switch_table(self):

        self.tui.db.create_table("table1", {"id": "int"})

        self.tui.db.create_table("table2", {"id": "int"})

        inputs = ["8", "table1", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Переключено на:", output)
                self.assertEqual(self.tui.db.get_current_name(), "table1")

    def test_search_records(self):

        self.tui.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

        table = self.tui.db.get_table()

        table.insert({"id": 1, "name": "Alex", "age": 20})

        inputs = ["9", "", "Alex", "", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Alex", output)

    def test_sort_records(self):

        self.tui.db.create_table("students", {"id": "int", "name": "str", "age": "int"})

        table = self.tui.db.get_table()

        table.insert({"id": 2, "name": "Bob", "age": 30})

        table.insert({"id": 1, "name": "Alex", "age": 20})

        inputs = ["7", "id", "asc", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Alex", output)
                self.assertIn("Bob", output)

    def test_value_error(self):

        inputs = ["1", "students", "abc", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Ошибка ввода числа", output)

    def test_database_error(self):

        inputs = ["3", "0"]

        with patch("builtins.input", side_effect=inputs):
            with patch("sys.stdout", new=StringIO()) as fake_out:

                self.tui.run()

                output = fake_out.getvalue()

                self.assertIn("Ошибка:", output)
