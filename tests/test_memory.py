import unittest

from src.db.backend.memory import Database
from src.db.backend.errors import (
    TableAlreadyExistsError,
    TableNotCreatedError,
    EmptyTableError,
    InvalidFieldError,
    ValidationError,
)


class TestMemory(unittest.TestCase):

    def setUp(self):

        self.db = Database()

        self.db.create_table("books", {
            "title": "str",
            "year": "int",
            "pages": "int"
        })

        self.table = self.db.get_table()

    #  CREATE RECORD 

    def test_create_record(self):

        cases = [
            {"title": "Book1", "year": 2000, "pages": 100},
            {"title": "Book2", "year": 2005, "pages": 200},
            {"title": "Book3", "year": 2010, "pages": 300},
            {"title": "Book4", "year": 2015, "pages": 400},
        ]

        for case in cases:
            with self.subTest(case=case):
                self.table.insert(case)
                self.assertIn(case, self.table.rows)

    #  EMPTY TABLE 

    def test_empty_table_select(self):

        db = Database()
        db.create_table("books", {"a": "str"})
        table = db.get_table()

        with self.assertRaises(EmptyTableError):
            table.select()

    #  SELECT / FILTER 

    def test_select_and_filter(self):

        data = [
            {"title": "A", "year": 2000, "pages": 100},
            {"title": "B", "year": 2005, "pages": 200},
            {"title": "C", "year": 2000, "pages": 300},
        ]

        for d in data:
            self.table.insert(d)

        cases = [
            {
                "name": "без фильтра",
                "expected": data
            },
            {
                "name": "по году",
                "filter": {"year": 2000},
                "expected": [data[0], data[2]]
            },
            {
                "name": "по названию",
                "filter": {"title": "B"},
                "expected": [data[1]]
            },
        ]

        for case in cases:

            with self.subTest(name=case["name"]):

                if "filter" in case:
                    result = [
                        r for r in self.table.rows
                        if all(str(r[k]) == str(v) for k, v in case["filter"].items())
                    ]
                else:
                    result = self.table.rows

                self.assertEqual(result, case["expected"])

    #  SORT 

    def test_sort(self):

        data = [
            {"title": "A", "year": 2010},
            {"title": "B", "year": 2000},
            {"title": "C", "year": 2020},
        ]

        for d in data:
            self.table.insert(d)

        result = self.table.sort("year", asc=True)

        self.assertEqual(
            [r["year"] for r in result],
            [2000, 2010, 2020]
        )

    #  INVALID FIELD 

    def test_invalid_field_sort(self):

        self.table.insert({"title": "A", "year": 2000})

        with self.assertRaises(InvalidFieldError):
            self.table.sort("wrong_field")

    #  UPDATE 

    def test_update(self):

        self.table.insert({"title": "A", "year": 2000})

        updated = self.table.update(
            {"title": "A"},
            {"year": 2025}
        )

        self.assertEqual(updated, 1)
        self.assertEqual(self.table.rows[0]["year"], 2025)

    def test_update_not_found(self):

        with self.assertRaises(ValidationError):
            self.table.update({"title": "X"}, {"year": 999})

    # DELETE 

    def test_delete(self):

        self.table.insert({"title": "A"})
        self.table.insert({"title": "B"})

        deleted = self.table.delete({"title": "A"})

        self.assertEqual(deleted, 1)
        self.assertEqual(len(self.table.rows), 1)

    def test_delete_all(self):

        self.table.insert({"title": "A"})
        self.table.insert({"title": "B"})

        deleted = self.table.delete({})

        self.assertEqual(deleted, 2)
        self.assertEqual(len(self.table.rows), 0)

    #  MULTIPLE TABLES 

    def test_table_switch(self):

        self.db.create_table("users", {"name": "str"})
        self.db.switch_table("users")

        self.assertEqual(self.db.get_current_name(), "users")

    def test_table_already_exists(self):

        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("books", {"x": "str"})


if __name__ == "__main__":
    unittest.main()