class DatabaseError(Exception):
    pass


class TableNotCreatedError(DatabaseError):
    def __init__(self):
        super().__init__("Таблица не создана.")


class TableAlreadyExistsError(DatabaseError):
    def __init__(self, name):
        super().__init__(f"Таблица '{name}' уже существует.")


class EmptyTableError(DatabaseError):
    def __init__(self):
        super().__init__("Таблица пустая.")


class EmptyFieldError(DatabaseError):
    def __init__(self):
        super().__init__("Поле не может быть пустым.")


class InvalidFieldError(DatabaseError):
    def __init__(self, field):
        super().__init__(f"Поле '{field}' некорректно.")


class InvalidTypeError(DatabaseError):
    def __init__(self, field, expected):
        super().__init__(f"Ошибка типа поля '{field}'. Ожидается {expected}.")


class ValidationError(DatabaseError):
    def __init__(self, msg="Ошибка валидации"):
        super().__init__(msg)


class InvalidSchemaError(DatabaseError):
    def __init__(self, field):
        super().__init__(f"Некорректное имя поля: '{field}'")


class RecordNotFoundError(DatabaseError):
    def __init__(self):
        super().__init__("Записи не найдены.")
