from .backend.errors import DatabaseError
from .backend.file_csv import CsvFileDatabase
from .backend.file_json import JsonFileDatabase
from .backend.memory import Database


class TUI:
    def __init__(self):
        print("Выберите тип базы данных:")
        print("1. In-memory")
        print("2. JSON file database")
        print("3. CSV file database")

        choice = input(">>> ").strip()

        if choice == "2":
            self.db = JsonFileDatabase()
        elif choice == "3":
            self.db = CsvFileDatabase()
        else:
            self.db = Database()

    def run(self):
        while True:
            print("\n=== МЕНЮ ===")
            print("Текущая таблица:", self.db.get_current_name())
            print("1. Создать таблицу")
            print("2. Добавить запись")
            print("3. Показать записи")
            print("4. Обновить запись")
            print("5. Удалить запись")
            print("6. Список таблиц")
            print("7. Сортировка")
            print("8. Переключить таблицу")
            print("9. Поиск")
            print("0. Выход")

            c = input(">>> ").strip()

            try:
                if c == "1":
                    name = input("Имя таблицы: ").strip()
                    n = int(input("Количество полей: "))
                    schema = {}

                    for _ in range(n):
                        f = input("Имя поля: ").strip()
                        t = input("Тип (int/float/str): ").strip()
                        schema[f] = t

                    self.db.create_table(name, schema)
                    print("Создано.")

                elif c == "2":
                    table = self.db.get_table()
                    record = {}
                    print("\nДобавление:")

                    for field, ftype in table.schema.items():
                        while True:
                            value = input(f"{field} [{ftype}]: ")

                            try:
                                record[field] = table.validate(field, value)
                                break
                            except DatabaseError as e:
                                print(e)

                    table.insert(record)
                    self.db.save_current()
                    print("Запись добавлена.")

                elif c == "3":
                    table = self.db.get_table()

                    for r in table.select():
                        print(r)

                elif c == "4":
                    table = self.db.get_table()
                    print("\n=== ОБНОВЛЕНИЕ ===")

                    fk = input("Фильтр поле по полю (Enter = пропустить): ").strip()
                    fv = input("Значение поля (Enter = пропустить): ").strip()
                    val = input("Фильтр по значению (Enter = пропустить): ").strip()
                    uk = input("Поле изменения: ").strip()
                    uv = input("Новое значение: ").strip()

                    filters = {}
                    if fk and fv:
                        filters[fk] = fv

                    value_filter = val if val != "" else None
                    updated = table.update(
                        filters=filters if filters else None,
                        value_filter=value_filter,
                        updates={uk: uv},
                    )
                    self.db.save_current()
                    print("Обновлено:", updated)

                elif c == "5":
                    table = self.db.get_table()
                    print("\n=== УДАЛЕНИЕ ===")

                    fk = input("Фильтр поле (Enter = пропустить): ").strip()
                    fv = input("Значение поля (Enter = пропустить): ").strip()
                    val = input("Удалить по значению (Enter = пропустить): ").strip()

                    filters = {}
                    if fk and fv:
                        filters[fk] = fv

                    value_filter = val if val != "" else None
                    deleted = table.delete(
                        filters=filters if filters else None,
                        value_filter=value_filter,
                    )
                    self.db.save_current()
                    print("Удалено:", deleted)

                elif c == "6":
                    print(self.db.list_tables())

                elif c == "7":
                    table = self.db.get_table()
                    f = input("Поле сортировки: ").strip()
                    o = input("asc/desc (Enter = asc): ").strip()
                    asc = o != "desc"

                    for r in table.sort(f, asc):
                        print(r)

                elif c == "8":
                    name = input("Имя таблицы: ").strip()
                    self.db.switch_table(name)
                    print("Переключено на:", name)

                elif c == "9":
                    table = self.db.get_table()
                    print("Поиск (Enter = пропустить поле)")
                    filters = {}

                    for field in table.schema:
                        v = input(f"{field}: ")
                        if v:
                            filters[field] = v

                    for r in table.search(filters):
                        print(r)

                elif c == "0":
                    self.db.save_all()
                    print("Выход")
                    break

            except DatabaseError as e:
                print("Ошибка:", e)

            except ValueError:
                print("Ошибка ввода числа")
