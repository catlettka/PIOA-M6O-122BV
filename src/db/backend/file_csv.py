import csv
from pathlib import Path

from .errors import (
    DatabaseError,
    FileStorageError,
    InvalidSchemaError,
    InvalidStorageDataError,
    InvalidTypeError,
    TableNotCreatedError,
)
from .memory import Database, Table


class CsvFileDatabase(Database):
    """
    Файловая база данных в CSV-формате.

    Формат файла:
    1-я строка: __schema__,id:int,name:str
    2-я строка: id,name
    Далее записи таблицы.
    """

    SCHEMA_MARKER = "__schema__"

    def __init__(self, directory="data_csv"):
        super().__init__()
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._load_all_tables()

    # создаёт новую таблицу и сразу сохраняет её в csv-файл
    def create_table(self, name, schema):
        self._validate_table_name(name)
        super().create_table(name, schema)
        self._save_table(name.strip())

    # сохраняет текущую активную таблицу в csv-файл
    def save_current(self):
        if self.current is None:
            raise TableNotCreatedError()

        self._save_table(self.current)

    # сохраняет все таблицы базы данных в csv-файлы
    def save_all(self):
        for table_name in self.tables:
            self._save_table(table_name)

    # проверяет имя таблицы, чтобы в нём не было символов пути
    def _validate_table_name(self, name):
        if any(separator in name for separator in ("/", "\\")):
            raise InvalidSchemaError(name)

    # возвращает путь к csv-файлу таблиц
    def _get_table_path(self, table_name):
        self._validate_table_name(table_name)
        return self.directory / f"{table_name}.csv"

    # сохраняет указанную таблицу в отдельный csv-файл
    def _save_table(self, table_name):
        if table_name not in self.tables:
            raise TableNotCreatedError()

        table = self.tables[table_name]
        schema_row = [self.SCHEMA_MARKER]
        schema_row.extend(
            f"{field}:{field_type}" for field, field_type in table.schema.items()
        )
        header_row = list(table.schema.keys())

        try:
            with self._get_table_path(table_name).open(
                "w", encoding="utf-8", newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerow(schema_row)
                writer.writerow(header_row)

                for row in table.rows:
                    writer.writerow([row[field] for field in header_row])
        except OSError as error:
            raise FileStorageError("Не удалось сохранить CSV-файл таблицы.") from error

    # загружает все csv-файлы из папки хранилища
    def _load_all_tables(self):
        try:
            paths = sorted(self.directory.glob("*.csv"))
        except OSError as error:
            raise FileStorageError(
                "Не удалось прочитать каталог с CSV-таблицами."
            ) from error

        for path in paths:
            table = self._load_table_from_path(path)
            self.tables[table.name] = table

        if self.tables:
            self.current = next(iter(self.tables))

    # загружает одну таблицу из csv-файла и проверяет её данные
    def _load_table_from_path(self, path):
        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.reader(file))
        except OSError as error:
            raise FileStorageError(
                f"Не удалось прочитать файл '{path.name}'."
            ) from error

        if len(rows) < 2:
            raise InvalidStorageDataError(
                f"Файл '{path.name}' имеет неполную структуру."
            )

        schema_row = rows[0]
        header_row = rows[1]

        if not schema_row or schema_row[0] != self.SCHEMA_MARKER:
            raise InvalidStorageDataError(
                f"Файл '{path.name}' должен начинаться со строки схемы."
            )

        schema = self._parse_schema_row(schema_row[1:], path.name)

        if list(schema.keys()) != header_row:
            raise InvalidStorageDataError(
                f"В файле '{path.name}' заголовок не совпадает со схемой."
            )

        table = Table(path.stem, schema)

        try:
            for values in rows[2:]:
                if len(values) != len(header_row):
                    raise InvalidStorageDataError(
                        f"В файле '{path.name}' запись имеет неверное количество полей."
                    )

                record = dict(zip(header_row, values))
                table.insert(record)
        except DatabaseError as error:
            raise InvalidStorageDataError(
                f"В файле '{path.name}' записи не соответствуют схеме."
            ) from error

        return table

    # разбирает строку схемы csv-файла
    def _parse_schema_row(self, cells, file_name):
        schema = {}

        for cell in cells:
            field, separator, field_type = cell.partition(":")

            if separator != ":" or not field or not field_type:
                raise InvalidStorageDataError(
                    f"В файле '{file_name}' некорректное описание поля '{cell}'."
                )

            if field_type not in Table.ALLOWED_TYPES:
                raise InvalidTypeError(field, "int/float/str")

            schema[field] = field_type

        return schema
