from .backend.memory import Database
from .backend.errors import DatabaseError


class TUI:

    def __init__(self):
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
                # создает новую таблицу
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

                # добавление новой записи в базу данных
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
                    print("Запись добавлена.")

                # вывод списка записей
                elif c == "3":

                    table = self.db.get_table()

                    for r in table.select():
                        print(r)

                # обновления поля существующей записи по идентификатору или фильтру
                elif c == "4":

                    table = self.db.get_table()

                    print("\n=== ОБНОВЛЕНИЕ ===")

                    fk = input(
                        "Фильтр поле по полю(Enter = пропустить, перейти к фильтру по значению): "
                    ).strip()
                    fv = input(
                        "Значение поля(Enter = пропустить, перейти к фильтру по значению): "
                    ).strip()

                    val = input(
                        "Фильтр по значению (Enter = пропустить, если был использован фильтр по полю): "
                    ).strip()

                    uk = input("Поле изменения: ").strip()
                    uv = input("Новое значение: ").strip()

                    # ФИЛЬТР ПО ПОЛЯМ
                    filters = {}
                    if fk and fv:
                        filters[fk] = fv

                    value_filter = val if val != "" else None

                    updated = table.update(
                        filters=filters if filters else None,
                        value_filter=value_filter,
                        updates={uk: uv},
                    )

                    print("Обновлено:", updated)

                # удаления записи
                elif c == "5":

                    table = self.db.get_table()

                    print("\n=== УДАЛЕНИЕ ===")

                    fk = input(
                        "Фильтр поле (Enter = пропустить, перейти к удалению по значению): "
                    ).strip()
                    fv = input(
                        "Значение поля(Enter = пропустить, перейти к удалению по значению): "
                    ).strip()

                    val = input(
                        "Удалить по значению(Enter = пропустить, если было использовано удаление по полю): "
                    ).strip()

                    filters = {}
                    if fk and fv:
                        filters[fk] = fv

                    value_filter = val if val != "" else None

                    deleted = table.delete(
                        filters=filters if filters else None, value_filter=value_filter
                    )

                    print("Удалено:", deleted)

                # отображение всех таблиц
                elif c == "6":
                    print(self.db.list_tables())

                # сортировка таблицы
                elif c == "7":

                    table = self.db.get_table()

                    f = input("Поле сортировки: ")
                    o = input(
                        "asc/desc(по возрастанию/по убыванию) (Enter = asc): "
                    ).strip()

                    asc = o != "desc"

                    for r in table.sort(f, asc):
                        print(r)

                # переключение таблицы
                elif c == "8":

                    name = input("Имя таблицы: ")
                    self.db.switch_table(name)
                    print("Переключено на:", name)

                # поиск записи
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

                # выход из программы
                elif c == "0":
                    print("Выход")
                    break

            except DatabaseError as e:
                print("Ошибка:", e)

            except ValueError:
                print("Ошибка ввода числа")
