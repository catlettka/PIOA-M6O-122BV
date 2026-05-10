from .errors import *


class Table:
    """
    Класс Table — представляет одну таблицу в базе данных.
    Хранит:
    - schema (структура таблицы)
    - rows (записи)
    """
    # инициализация таблицы
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema
        self.rows = []

    # добовление записи в таблицу
    def insert(self, record):
        self.rows.append(record)

    # получение всех записей таблицы
    def select(self):

        if not self.rows:
            raise EmptyTableError()

        return self.rows

    # сортировка записей по указанному полю
    def sort(self, field, asc=True):

        if field not in self.schema:
            raise InvalidFieldError(field)

        return sorted(
            self.rows,
            key=lambda x: x[field],
            reverse=not asc
        )

    # обновление записей по фильтру
    def update(self, filters, updates):

        count = 0

        for r in self.rows:

            if all(str(r.get(k)) == str(v) for k, v in filters.items()):

                for k, v in updates.items():

                    if k not in self.schema:
                        raise InvalidFieldError(k)

                    r[k] = v

                count += 1

        if count == 0:
            raise ValidationError("Записи не найдены")

        return count

    # удаление записей по фильтру
    def delete(self, filters):

        if not filters:
            before = len(self.rows)
            self.rows.clear()
            return before

        before = len(self.rows)

        self.rows = [
            r for r in self.rows
            if not all(str(r.get(k)) == str(v) for k, v in filters.items())
        ]

        if before == len(self.rows):
            raise ValidationError("Записи не найдены")

        return before - len(self.rows)


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

        if name in self.tables:
            raise TableAlreadyExistsError(name)

        self.tables[name] = Table(name, schema)
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