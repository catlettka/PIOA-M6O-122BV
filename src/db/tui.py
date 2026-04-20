# Импортируем из модуля backend.memory функции, реализующие операции
# создания записи и выборки записей из таблицы.
from .backend.memory import  (
    create_db,
    create_table,
    use_table,
    list_tables,
    create_record,
    select_record,
    update_record,
    delete_record,
)

# создание базы таблиц(dict)
db = create_db()

# создает новую таблицу
def _create_table():
    name = input("Название таблицы: ").strip()

    try:
        create_table(db, name)
        print("Таблица создана")
    except ValueError as e:
        print("Ошибка:", e)

# переключает активную таблицу
def _switch_table():
    name = input("Имя таблицы: ").strip()

    try:
        use_table(db, name)
        print("Текущая таблица:", name)
    except ValueError as e:
        print("Ошибка:", e)

# возвращает текущую таблицу
def _show_tables():
    tables = list_tables(db)

    if not tables:
        print("Таблиц нет")
        return

    print("Таблицы:")
    for t in tables:
        print("-", t)

# Функция вывода текстового меню в консоль.
def _print_menu() -> None:
    # Символ \n обозначает перевод строки.
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить запись")  
    print("5. Удалить запись")
    print("6. Создать таблицу")
    print("7. Выбрать таблицу")
    print("8. Показать таблицы")
    print("0. Выход")

# Функция чтения целочисленного значения из консоли.
def _read_int(prompt: str) -> int:
    # Используется цикл с повторением до получения корректного ввода.
    while True:
        # Получение строки из консоли с удалением пробельных символов
        # в начале и в конце строки.
        raw = input(prompt).strip()
        try:
            # Преобразование строки к целому числу.
            return int(raw)
        except ValueError:
            # Исключение возникает при невозможности преобразования.
            # Пользователю выводится сообщение об ошибке,
            # после чего ввод повторяется.
            print("Ошибка: введите целое число.")

# Функция добавления новой записи в базу данных.
def _add_student() -> None:
    print("\nДобавление записи")
    student_id = _read_int("id: ")
    first_name = input("first_name: ").strip()
    second_name = input("second_name: ").strip()
    age = _read_int("age: ")
    sex = input("sex: ").strip()

    try:
        # Вызов функции слоя бизнес-логики.
        record = create_record(db, student_id, first_name, second_name, age, sex)

        # В случае успешного добавления запись выводится в консоль.
        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        # Обработка ошибок валидации.
        print(f"Ошибка: {exc}")

# Вспомогательная функция вывода списка записей.
def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    # Проверка на пустой список.
    if not records:
        print("Записи не найдены.")
        return

    # Последовательный вывод записей.
    for record in records:
        print(record)

# Функция вывода всех записей из базы данных.
def _show_all_students() -> None:
    print("\nСписок записей")
    _print_records(select_record(db))

# Функция чтения необязательного целочисленного значения.
# Пустой ввод интерпретируется как отсутствие фильтра (None).
def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")

# Функция поиска записей по заданным фильтрам.
def _find_students_by_filter() -> None:
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    student_id = _read_optional_int("id: ")

    # Оператор `or` возвращает первое истинное значение.
    # Если строка после strip() пуста, будет возвращено None.
    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None

    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None

    records = select_record(
        db,
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex,
    )

    _print_records(records)

# Функция обновления поля существующей записи по идентификатору или фильтру.
def _update_student() -> None:
    print("\nОбновление записи (Enter = пропустить поле)")

    student_id = _read_int("id: ")

    print("Оставь поле пустым, чтобы не изменять")

    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None

    age = _read_optional_int("age: ")

    sex = input("sex: ").strip() or None

    try:
        record = update_record(
            db,
            student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )
        print(f"Обновлено: {record}")

    except ValueError as exc:
        print(f"Ошибка: {exc}")

#Функция удаления записи из таблицы по идентификатору или фильтру
def _delete_student() -> None:
    print("\nУдаление записи (Enter = пропустить поле)")

    student_id = _read_optional_int("id: ")

    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None
    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None

    count = delete_record(
        db,
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex,
    )

    if count > 0:
        print(f"Удалено записей: {count}")
    else:
        print("Ничего не найдено для удаления.")

def run() -> None:
    """
    Запускает основной цикл текстового пользовательского интерфейса.

    Цикл выполняется до тех пор, пока пользователь явно
    не выберет завершение программы.
    """
    while True:
        # Отображение меню доступных действий.
        _print_menu()

        # Получение команды пользователя.
        # Метод strip() удаляет пробельные символы
        # в начале и в конце строки.
        action = input("Выберите действие: ").strip()

        # Диспетчеризация пользовательской команды.
        if action == "1":
            _add_student()

        elif action == "2":
            _show_all_students()

        elif action == "3":
            _find_students_by_filter()
            
        elif action == "4":
            _update_student()

        elif action == "5":
            _delete_student()

        elif action == "6":
            _create_table()

        elif action == "7":
            _switch_table()

        elif action == "8":
            _show_tables()

        elif action == "0":
            # Завершение работы программы.
            print("Выход из программы.")
            break

        else:
            # Обработка некорректного ввода команды.
            print("Неизвестная команда. Повторите ввод.")
