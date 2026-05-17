import pytest
from unittest.mock import MagicMock, patch
from src.db.tui import TUI
from src.db.backend.errors import DatabaseError


def make_tui():
    tui = TUI()
    tui.db = MagicMock()
    return tui
    
def test_create_table():
    tui = make_tui()

    with patch("builtins.input", side_effect=[
        "1",
        "users",
        "2",
        "id", "int",
        "name", "str",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        tui.db.create_table.assert_called_once()

def test_insert():
    tui = make_tui()

    table = MagicMock()
    table.schema = {"id": "int", "name": "str"}
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=[
        "2",
        "1", "test",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        table.insert.assert_called_once()

def test_show():
    tui = make_tui()

    table = MagicMock()
    table.select.return_value = [{"id": 1}]
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=["3", "0"]), \
         patch("builtins.print"):

        tui.run()

        table.select.assert_called()

def test_update():
    tui = make_tui()

    table = MagicMock()
    table.schema = {"name": "str"}
    table.update.return_value = 1
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=[
        "4",
        "", "",
        "name",
        "new",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        table.update.assert_called()

def test_delete_yes():
    tui = make_tui()

    table = MagicMock()
    table.delete.return_value = 2
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=[
        "5",
        "", "",
        "yes",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        table.delete.assert_called()

def test_delete_cancel():
    tui = make_tui()

    table = MagicMock()
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=[
        "5",
        "", "",
        "no",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        table.delete.assert_not_called()

def test_list_tables():
    tui = make_tui()
    tui.db.list_tables.return_value = ["users"]

    with patch("builtins.input", side_effect=["6", "0"]), \
         patch("builtins.print") as p:

        tui.run()

        assert any("users" in str(x) for x in p.call_args_list)

def test_sort():
    tui = make_tui()

    table = MagicMock()
    table.sort.return_value = [{"id": 1}]
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=[
        "7",
        "id",
        "",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        table.sort.assert_called()

def test_switch():
    tui = make_tui()

    with patch("builtins.input", side_effect=[
        "8",
        "users",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        tui.db.switch_table.assert_called_with("users")

def test_search():
    tui = make_tui()

    table = MagicMock()
    table.schema = {"id": "int"}
    table.search.return_value = [{"id": 1}]
    tui.db.get_table.return_value = table

    with patch("builtins.input", side_effect=[
        "9",
        "1",
        "0"
    ]), patch("builtins.print"):

        tui.run()

        table.search.assert_called()

def test_db_error():
    tui = make_tui()
    tui.db.get_table.side_effect = DatabaseError("fail")

    with patch("builtins.input", side_effect=["3", "0"]), \
         patch("builtins.print"):

        tui.run()