import sys
from .backend import memory

def input_text(prompt: str) -> str:

    while True:

        value = input(prompt).strip()

        if value:
            return value

        print("Ошибка: пустое значение")


def input_int(prompt: str) -> int:

    while True:

        value = input(prompt).strip()

        if not value:
            print("Ошибка: введите число")
            continue

        if not value.isdigit():
            print("Ошибка: нужно целое число")
            continue

        return int(value)


def input_type(prompt: str) -> type:

    types = {
        "int": int,
        "str": str,
        "float": float
    }

    while True:

        value = input(prompt).strip()

        if value not in types:
            print("Ошибка: только int/str/float")
            continue

        return types[value]


def input_typed(field: str, t: type):

    while True:

        raw = input(f"{field} ({t.__name__}): ").strip()

        try:

            if t == int:
                return int(raw)

            if t == float:
                return float(raw)

            return raw

        except ValueError:
            print(f"Ошибка: нужен тип {t.__name__}")

def print_records(records):

    if not records:
        print("Пусто")
        return

    for record in records:
        print(record)

def menu():

    print("\n=== БАЗА ДАННЫХ ===")
    print("1. Создать таблицу")
    print("2. Выбрать таблицу")
    print("3. Добавить запись")
    print("4. Показать записи")
    print("5. Найти записи")
    print("6. Обновить записи")
    print("7. Удалить записи")
    print("8. Список таблиц")
    print("0. Выход")

def create_table():

    name = input_text("Имя таблицы: ")

    count = input_int("Количество полей: ")

    schema = {}

    for i in range(count):

        print(f"\nПоле {i + 1}")

        field = input_text("Имя поля: ")

        if field in schema:
            print("Ошибка: поле уже существует")
            return

        field_type = input_type("Тип (int/str/float): ")

        schema[field] = field_type

    memory.create_table(name, schema)

    print("Таблица создана")

def use_table():

    name = input_text("Имя таблицы: ")

    try:
        memory.use_table(name)
        print(f"Текущая таблица: {name}")

    except Exception as e:
        print("Ошибка:", e)

def add():

    table = memory.get_current_table()

    schema = memory.SCHEMAS[table]

    data = {}

    for field, field_type in schema.items():

        value = input_typed(field, field_type)

        data[field] = value

    record = memory.create_record(table, **data)

    print("Добавлено:")
    print(record)

def show():

    table = memory.get_current_table()

    records = memory.select_record(table)

    print("\n=== ЗАПИСИ ===")

    print_records(records)

def find():

    table = memory.get_current_table()

    schema = memory.SCHEMAS[table]

    filters = {}

    print("\nВведите фильтр")
    print("Enter = пропустить")

    for field, field_type in schema.items():

        raw = input(f"{field} ({field_type.__name__}): ").strip()

        if not raw:
            continue

        try:

            if field_type == int:
                filters[field] = int(raw)

            elif field_type == float:
                filters[field] = float(raw)

            else:
                filters[field] = raw

        except ValueError:
            print(f"Ошибка: нужен тип {field_type.__name__}")
            return

    records = memory.select_record(table, **filters)

    print_records(records)

def update():

    table = memory.get_current_table()

    schema = memory.SCHEMAS[table]

    filters = {}
    updates = {}

    print("\nФИЛЬТР")
    print("Enter = пропустить")

    for field, field_type in schema.items():

        raw = input(f"{field} ({field_type.__name__}): ").strip()

        if not raw:
            continue

        try:

            if field_type == int:
                filters[field] = int(raw)

            elif field_type == float:
                filters[field] = float(raw)

            else:
                filters[field] = raw

        except ValueError:
            print(f"Ошибка: нужен тип {field_type.__name__}")
            return

    print("\nНОВЫЕ ЗНАЧЕНИЯ")
    print("Enter = пропустить")

    for field, field_type in schema.items():

        raw = input(f"{field} ({field_type.__name__}): ").strip()

        if not raw:
            continue

        try:

            if field_type == int:
                updates[field] = int(raw)

            elif field_type == float:
                updates[field] = float(raw)

            else:
                updates[field] = raw

        except ValueError:
            print(f"Ошибка: нужен тип {field_type.__name__}")
            return

    updated = memory.update_record(table, filters, updates)

    print(f"Обновлено записей: {updated}")

def delete():

    table = memory.get_current_table()

    schema = memory.SCHEMAS[table]

    filters = {}

    print("\nФИЛЬТР")
    print("Enter = пропустить")

    for field, field_type in schema.items():

        raw = input(f"{field} ({field_type.__name__}): ").strip()

        if not raw:
            continue

        try:

            if field_type == int:
                filters[field] = int(raw)

            elif field_type == float:
                filters[field] = float(raw)

            else:
                filters[field] = raw

        except ValueError:
            print(f"Ошибка: нужен тип {field_type.__name__}")
            return

    deleted = memory.delete_record(table, **filters)

    print(f"Удалено записей: {deleted}")

def show_tables():

    tables = memory.list_tables()

    print("\n=== ТАБЛИЦЫ ===")

    if not tables:
        print("Пусто")
        return

    for name, info in tables.items():

        schema = ", ".join(
            f"{k}:{v.__name__}"
            for k, v in info["schema"].items()
        )

        print(f"\n{name}")
        print(f"Схема: {schema}")
        print(f"Записей: {info['count']}")

def run():

    while True:

        menu()

        choice = input("> ").strip()

        try:

            if choice == "1":
                create_table()

            elif choice == "2":
                use_table()

            elif choice == "3":
                add()

            elif choice == "4":
                show()

            elif choice == "5":
                find()

            elif choice == "6":
                update()

            elif choice == "7":
                delete()

            elif choice == "8":
                show_tables()

            elif choice == "0":
                print("Выход")
                sys.exit()

            else:
                print("Ошибка: выберите 0-8")

        except Exception as e:
            print("Ошибка:", e)