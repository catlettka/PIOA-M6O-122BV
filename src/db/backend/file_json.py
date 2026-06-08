import json
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


class JsonFileDatabase(Database):
    """Файловая база данных, сохраняющая каждую таблицу в отдельный JSON-файл."""

    # создаёт JSON-хранилище, создаёт папку data_json и загружает таблицы
    def __init__(self, directory="data_json"):
        super().__init__()
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._load_all_tables()

    # создаёт новую таблицу и сразу сохраняет её в JSON-файл
    def create_table(self, name, schema):
        self._validate_table_name(name)
        super().create_table(name, schema)
        self._save_table(name.strip())

    # сохраняет текущую активную таблицу в json-файл
    def save_current(self):
        if self.current is None:
            raise TableNotCreatedError()

        self._save_table(self.current)

    # сохраняет все таблицы базы данных в JSON-файлы
    def save_all(self):
        for table_name in self.tables:
            self._save_table(table_name)

    # проверяет имя таблицы, чтобы в нём не было символов пути
    def _validate_table_name(self, name):
        if any(separator in name for separator in ("/", "\\")):
            raise InvalidSchemaError(name)

    # возвращает путь к JSON-файлу таблицы
    def _get_table_path(self, table_name):
        self._validate_table_name(table_name)
        return self.directory / f"{table_name}.json"

    # сохраняет указанную таблицу в отдельный JSON-файл
    def _save_table(self, table_name):
        if table_name not in self.tables:
            raise TableNotCreatedError()

        table = self.tables[table_name]
        data = {
            "name": table.name,
            "schema": table.schema,
            "records": table.select(),
        }

        try:
            with self._get_table_path(table_name).open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except OSError as error:
            raise FileStorageError("Не удалось сохранить JSON-файл таблицы.") from error

    # загружает все JSON-файлы из папки хранилища
    def _load_all_tables(self):
        try:
            paths = sorted(self.directory.glob("*.json"))
        except OSError as error:
            raise FileStorageError(
                "Не удалось прочитать каталог с JSON-таблицами."
            ) from error

        for path in paths:
            table = self._load_table_from_path(path)
            self.tables[table.name] = table

        if self.tables:
            self.current = next(iter(self.tables))

    # загружает одну таблицу из JSON-файла и проверяет её данные
    def _load_table_from_path(self, path):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                f"Файл '{path.name}' содержит некорректный JSON."
            ) from error
        except OSError as error:
            raise FileStorageError(
                f"Не удалось прочитать файл '{path.name}'."
            ) from error

        if not isinstance(data, dict):
            raise InvalidStorageDataError(
                f"Файл '{path.name}' должен содержать объект JSON."
            )

        name = data.get("name", path.stem)
        schema = data.get("schema")
        records = data.get("records", [])

        if not isinstance(name, str) or not name.strip():
            raise InvalidStorageDataError(
                f"В файле '{path.name}' некорректное имя таблицы."
            )

        if not isinstance(schema, dict):
            raise InvalidStorageDataError(f"В файле '{path.name}' некорректная схема.")

        if not isinstance(records, list):
            raise InvalidStorageDataError(
                f"В файле '{path.name}' records должен быть списком."
            )

        table = Table(name.strip(), self._validate_schema_from_storage(schema))

        try:
            for record in records:
                if not isinstance(record, dict):
                    raise InvalidStorageDataError(
                        f"В файле '{path.name}' каждая запись должна быть словарём."
                    )
                table.insert(record)
        except DatabaseError as error:
            raise InvalidStorageDataError(
                f"В файле '{path.name}' записи не соответствуют схеме."
            ) from error

        return table

    # "проверяет схему таблицы, загруженную из JSON-файла
    def _validate_schema_from_storage(self, schema):
        result = {}

        for field, field_type in schema.items():
            if not isinstance(field, str) or not field.strip():
                raise InvalidStorageDataError("В файле найдено некорректное имя поля.")

            if field_type not in Table.ALLOWED_TYPES:
                raise InvalidTypeError(field, "int/float/str")

            result[field.strip()] = field_type

        return result
