from .errors import (
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


class Table:
    """
    Класс Table — представляет одну таблицу в базе данных.
    Хранит:
    - schema (структура таблицы)
    - rows (записи)
    """

    ALLOWED_TYPES = {"int", "float", "str"}

    # инициализация таблицы
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema
        self.rows = []

    # единая валидация
    def validate(self, field, value):

        if field not in self.schema:
            raise InvalidFieldError(field)

        expected = self.schema[field]

        if value == "" or value is None:
            raise EmptyFieldError()

        try:
            if expected == "int":
                return int(value)

            if expected == "float":
                return float(value)

            if expected == "str":
                if str(value).isdigit():
                    raise InvalidTypeError(
                        field, "строчка не может состоять только из цифр"
                    )
                return str(value)

        except (ValueError, TypeError):
            raise InvalidTypeError(field, expected)

    # добовление записи в таблицу
    def insert(self, record):

        validated = {}

        for field in self.schema:

            if field not in record:
                raise ValidationError(f"Нет поля '{field}'")

            validated[field] = self.validate(field, record[field])

        self.rows.append(validated)

    # получение всех записей таблицы
    def select(self):
        return self.rows

    # сортировка записей по указанному полю
    def sort(self, field, asc=True):

        if field not in self.schema:
            raise InvalidFieldError(field)

        if not self.rows:
            raise EmptyTableError()

        return sorted(self.rows, key=lambda x: x[field], reverse=not asc)

    # поиск записей по фильтрам
    def search(self, filters=None):

        if not self.rows:
            raise EmptyTableError()

        if not filters:
            return self.rows

        result = []

        for row in self.rows:

            ok = True

            for k, v in filters.items():

                if k not in self.schema:
                    raise InvalidFieldError(k)

                if row.get(k) != self.validate(k, v):
                    ok = False
                    break

            if ok:
                result.append(row)

        if not result:
            raise RecordNotFoundError()

        return result

    # обновление записей по фильтру
    def update(self, filters=None, value_filter=None, updates=None):

        if not self.rows:
            raise EmptyTableError()

        if not updates:
            raise ValidationError("Нет данных для обновления")

        validated_updates = {k: self.validate(k, v) for k, v in updates.items()}

        count = 0

        for row in self.rows:

            matched = True

            if filters:
                for k, v in filters.items():

                    if k not in self.schema:
                        raise InvalidFieldError(k)

                    if row.get(k) != self.validate(k, v):
                        matched = False
                        break

            if matched and value_filter is not None:

                found = False

                for v in row.values():
                    if str(v) == str(value_filter):
                        found = True
                        break

                if not found:
                    matched = False

            if matched:
                row.update(validated_updates)
                count += 1

        if count == 0:
            raise RecordNotFoundError()

        return count

    # удаление записей по фильтру
    def delete(self, filters=None, value_filter=None):

        if not self.rows:
            raise EmptyTableError()

        # удалить всё
        if not filters and value_filter is None:
            count = len(self.rows)
            self.rows.clear()
            return count

        before = len(self.rows)

        new_rows = []

        for row in self.rows:

            matched = True

            if filters:
                for k, v in filters.items():

                    if k not in self.schema:
                        raise InvalidFieldError(k)

                    if row.get(k) != self.validate(k, v):
                        matched = False
                        break

            if matched and value_filter is not None:

                found = False

                for v in row.values():
                    if str(v) == str(value_filter):
                        found = True
                        break

                if not found:
                    matched = False

            if not matched:
                new_rows.append(row)

        self.rows = new_rows

        deleted = before - len(self.rows)

        if deleted == 0:
            raise RecordNotFoundError()

        return deleted


class Database:
    """
    Класс Database — управляет всеми таблицами.
    """

    # создание пустой базы данных
    def __init__(self):
        self.tables = {}
        self.current = None

    # создание новой таблицы
    def create_table(self, name, schema):

        if not name or not name.strip():
            raise EmptyFieldError()

        name = name.strip()

        if name in self.tables:
            raise TableAlreadyExistsError(name)

        validated_schema = {}

        for field, field_type in schema.items():

            if not field or not field.strip():
                raise InvalidSchemaError(field)

            field = field.strip()

            if field_type not in Table.ALLOWED_TYPES:
                raise InvalidTypeError(field, "int/float/str")

            validated_schema[field] = field_type

        self.tables[name] = Table(name, validated_schema)
        self.current = name

    # переключение на другую таблицу
    def switch_table(self, name):

        if name not in self.tables:
            raise TableNotCreatedError()

        self.current = name

    # возвращает имя текущей таблицы
    def get_current_name(self):
        return self.current or "не выбрана"

    # получение текущей таблицы
    def get_table(self):

        if not self.tables or self.current is None:
            raise TableNotCreatedError()

        return self.tables[self.current]

    # список всех созданных таблиц
    def list_tables(self):

        if not self.tables:
            raise TableNotCreatedError()

        return list(self.tables.keys())
