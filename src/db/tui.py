from .backend.memory import Database
from .backend.errors import *


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
            print("0. Выход")

            c = input(">>> ")

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

                # добавление новой записи в базу данных
                elif c == "2":

                    table = self.db.get_table()
                    record = {}

                    for field, ttype in table.schema.items():

                        while True:

                            value = input(f"{field} ({ttype}): ").strip()

                            if value == "":
                                print("Ошибка: поле не может быть пустым.")
                                continue

                            try:

                                if ttype == "int":
                                    value = int(value)

                                elif ttype == "float":
                                    value = float(value)

                                else:
                                    if value.replace("-", "").replace(".", "").isdigit():
                                        print("Ошибка: строка не может быть числом.")
                                        continue
                                    value = str(value)

                                record[field] = value
                                break

                            except:
                                print(f"Ошибка типа поля '{field}'")

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

                    fk = input("Фильтр поле (Enter = пропустить): ").strip()
                    fv = input("Значение (Enter = пропустить): ").strip()

                    filters = {}
                    if fk and fv:
                        filters[fk] = fv

                    uk = input("Поле изменения: ").strip()

                    if uk not in table.schema:
                        print("Ошибка: поле не существует")
                        continue

                    uv = input(f"Новое значение ({table.schema[uk]}): ").strip()

                    if uv == "":
                        print("Ошибка: значение не может быть пустым")
                        continue

                    try:

                        if table.schema[uk] == "int":
                            uv = int(uv)
                        elif table.schema[uk] == "float":
                            uv = float(uv)
                        else:
                            uv = str(uv)

                    except:
                        print("Ошибка типа данных")
                        continue

                    print("Обновлено:", table.update(filters, {uk: uv}))

                # удаления записи 
                elif c == "5":

                    table = self.db.get_table()

                    k = input("Поле (Enter = пропустить): ").strip()
                    v = input("Значение (Enter = пропустить): ").strip()

                    filters = {}

                    if k and v:
                        filters[k] = v

                    if not filters:
                        confirm = input("Удалить ВСЕ записи? (yes/no): ").strip().lower()
                        if confirm != "yes":
                            print("Отмена")
                            continue

                    print("Удалено:", table.delete(filters))

                # отображение всех таблиц
                elif c == "6":
                    print(self.db.list_tables())

                # сортировка таблицы
                elif c == "7":

                    table = self.db.get_table()

                    f = input("Поле сортировки: ").strip()
                    o = input("asc/desc(по возрастанию/по убыванию) (Enter = asc): ").strip()

                    asc = o != "desc"

                    for r in table.sort(f, asc):
                        print(r)

                # переключение таблицы
                elif c == "8":

                    name = input("Имя таблицы: ").strip()
                    self.db.switch_table(name)
                    print("Переключено на:", name)

                # выход из программы 
                elif c == "0":
                    print("Выход")
                    break

            except DatabaseError as e:
                print("Ошибка:", e)

            except Exception:
                print("Ошибка: неверный ввод")