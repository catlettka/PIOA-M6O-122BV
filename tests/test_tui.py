import io
import unittest
from unittest.mock import patch
from src.db.backend.memory import Database
from src.db.tui import TUI


class TestTUI(unittest.TestCase):
    def create_tui(self, choice="1"):
        with patch("builtins.input", side_effect=[choice]), patch(
            "sys.stdout", new_callable=io.StringIO
        ):
            return TUI()

    def run_tui(self, inputs, choice="1"):
        tui = self.create_tui(choice)

        with patch("builtins.input", side_effect=inputs), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as output:
            tui.run()
            return output.getvalue()

    def test_init_selects_memory_database_by_default(self):
        tui = self.create_tui("1")
        self.assertIsInstance(tui.db, Database)

    def test_init_selects_json_database(self):
        with patch("src.db.tui.JsonFileDatabase") as fake_json:
            fake_json.return_value = object()
            with patch("builtins.input", side_effect=["2"]), patch(
                "sys.stdout", new_callable=io.StringIO
            ):
                tui = TUI()

        self.assertIs(tui.db, fake_json.return_value)

    def test_init_selects_csv_database(self):
        with patch("src.db.tui.CsvFileDatabase") as fake_csv:
            fake_csv.return_value = object()
            with patch("builtins.input", side_effect=["3"]), patch(
                "sys.stdout", new_callable=io.StringIO
            ):
                tui = TUI()

        self.assertIs(tui.db, fake_csv.return_value)

    def test_create_table_and_list_tables(self):
        output = self.run_tui(
            [
                "1",  # создать таблицу
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "6",  # список таблиц
                "0",  # выход
            ]
        )

        self.assertIn("Создано.", output)
        self.assertIn("students", output)
        self.assertIn("Выход", output)

    def test_add_and_show_record(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "3",
                "0",
            ]
        )

        self.assertIn("Запись добавлена.", output)
        self.assertIn("{'id': 1, 'name': 'Иван'}", output)

    def test_add_record_repeats_input_after_validation_error(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "abc",  # ошибка int
                "1",  # повторный ввод id
                "123",  # ошибка str: только цифры
                "Иван",  # повторный ввод name
                "3",
                "0",
            ]
        )

        self.assertIn("Ошибка типа поля 'id'", output)
        self.assertIn("Ошибка типа поля 'name'", output)
        self.assertIn("{'id': 1, 'name': 'Иван'}", output)

    def test_update_record_by_field_filter(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "4",
                "id",
                "1",
                "",
                "name",
                "Петр",
                "3",
                "0",
            ]
        )

        self.assertIn("Обновлено: 1", output)
        self.assertIn("{'id': 1, 'name': 'Петр'}", output)

    def test_update_record_by_value_filter(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "4",
                "",
                "",
                "Иван",
                "name",
                "Петр",
                "3",
                "0",
            ]
        )

        self.assertIn("Обновлено: 1", output)
        self.assertIn("Петр", output)

    def test_delete_record_by_field_filter(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "5",
                "id",
                "1",
                "",
                "0",
            ]
        )

        self.assertIn("Удалено: 1", output)

    def test_delete_record_by_value_filter(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "5",
                "",
                "",
                "Иван",
                "0",
            ]
        )

        self.assertIn("Удалено: 1", output)

    def test_sort_records_descending(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "2",
                "2",
                "Петр",
                "7",
                "id",
                "desc",
                "0",
            ]
        )

        self.assertIn("{'id': 2, 'name': 'Петр'}", output)
        self.assertIn("{'id': 1, 'name': 'Иван'}", output)

    def test_switch_table_and_search(self):
        output = self.run_tui(
            [
                "1",
                "students",
                "2",
                "id",
                "int",
                "name",
                "str",
                "2",
                "1",
                "Иван",
                "1",
                "teachers",
                "1",
                "id",
                "int",
                "8",
                "students",
                "9",
                "1",
                "",
                "0",
            ]
        )

        self.assertIn("Переключено на: students", output)
        self.assertIn("{'id': 1, 'name': 'Иван'}", output)

    def test_invalid_number_input(self):
        output = self.run_tui(["1", "students", "abc", "0"])

        self.assertIn("Ошибка ввода числа", output)

    def test_database_error_is_printed(self):
        output = self.run_tui(["2", "0"])

        self.assertIn("Ошибка:", output)
        self.assertIn("Таблица не создана", output)


if __name__ == "__main__":
    unittest.main()
