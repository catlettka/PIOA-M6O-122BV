# Определение пользовательского алиаса типа для записи таблицы.
# В качестве структуры записи используется кортеж,
# поскольку кортеж является неизменяемым типом данных.
# Структура записи Student: (id, first_name, second_name, age, sex)
type StudentRecord = tuple[int, str, str, int, str]


def create_db():
    """
    Создаёт словарь базу таблиц.

    db хранит:
    - tables: хранилище всех таблиц
    - current: текущая активная таблица
    """
    return {
        "tables": {},  # словарь таблиц (пока пустой)
        "current": None
    }

# создание новой таблицы
def create_table(db, name: str) -> None:
    
    if name in db["tables"]:
        raise ValueError("Таблица c таким именем уже существует")

    db["tables"][name] = []

    if db["current"] is None:
        db["current"] = name

# выбор текущей таблицы
def use_table(db, name: str) -> None:
    if name not in db["tables"]:
        raise ValueError("Таблица c таким именем не сущесвует")

    db["current"] = name

# переключение текущей таблицы
def get_table(db):
    if db["current"] is None:
        raise ValueError("Таблица не выбрана")

    return db["tables"][db["current"]]

# список таблиц
def list_tables(db):
    return list(db["tables"].keys())

# Добавляет новую запись в существующую таблицу
def create_record(
    db,                # Словарь всей базы данных
    student_id: int,   # Уникальный идентификатор записи
    first_name: str,   # Имя
    second_name: str,  # Фамилия
    age: int,          # Возраст
    sex: str,          # Пол
):
    table = get_table(db)
    """
    Создаёт новую запись и добавляет её в таблицу Student.

    Выполняется валидация возраста и проверка уникальности идентификатора.
    В случае нарушения условий возбуждается исключение ValueError.
    """
    # Проверка корректности возраста.
    # Возраст не может быть отрицательным значением.
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным.")

    # Проверка уникальности идентификатора.
    # Функция any() возвращает True, если хотя бы один элемент
    # последовательности удовлетворяет условию.
    if any(record[0] == student_id for record in table):
        raise ValueError(f"Запись с id={student_id} уже существует.")

    # Формирование новой записи.
    # Метод strip() удаляет пробельные символы
    # в начале и в конце строки.
    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )

    # Добавление записи в таблицу.
    table.append(new_record)

    # Возврат созданной записи.
    return new_record

# Возвращает записи, подходящие под запрос или фильтр
def select_record(
    db,
    student_id: int | None = None,   # Фильтр по идентификатору
    first_name: str | None = None,   # Фильтр по имени
    second_name: str | None = None,  # Фильтр по фамилии
    age: int | None = None,          # Фильтр по возрасту
    sex: str | None = None,          # Фильтр по полу
):
    table = get_table(db)

    # Проверка отсутствия всех фильтров.
    # В этом случае возвращается копия списка,
    # чтобы предотвратить изменение исходной таблицы
    # внешним кодом.
    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return table.copy()

    # Формирование результирующего списка.
    result = []

    # Итерация по всем записям таблицы.
    for record in table:

        # Проверка соответствия каждому фильтру.
        # Если фильтр задан и запись ему не соответствует,
        # выполняется переход к следующей итерации цикла.

        if student_id is not None and record[0] != student_id:
            continue

        if first_name is not None and record[1] != first_name:
            continue

        if second_name is not None and record[2] != second_name:
            continue

        if age is not None and record[3] != age:
            continue

        if sex is not None and record[4] != sex:
            continue

        # Если запись удовлетворяет всем заданным условиям,
        # она добавляется в результирующий список.
        result.append(record)

    # Возврат списка найденных записей.
    return result

# Обновляет поля существующей записи по идентификатору или фильтру
def update_record(
    db,
    student_id: int,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
):
    table = get_table(db)
    """
    Обновляет запись по student_id.
    Можно менять частично (только переданные поля).
    """

    for index, record in enumerate(table):

        if record[0] == student_id:

            # Берём текущие значения
            updated_record = list(record)

            # Обновляем только то, что передано
            if first_name is not None:
                updated_record[1] = first_name.strip()

            if second_name is not None:
                updated_record[2] = second_name.strip()

            if age is not None:
                if age < 0:
                    raise ValueError("Поле age не может быть отрицательным.")
                updated_record[3] = age

            if sex is not None:
                updated_record[4] = sex.strip()
            

            table[index] = tuple(updated_record)
            return table[index]

    raise ValueError(f"Запись с id={student_id} не найдена.")

# Удаляет запись из таблицы по идентификатору или фильтру
def delete_record(
    db,
    student_id: int | None = None,
    first_name: str | None = None,
    second_name: str | None = None,
    age: int | None = None,
    sex: str | None = None,
) -> int:
    """
    Удаляет записи по id или фильтру.
    Возвращает количество удалённых записей.
    """

    table = get_table(db)
    deleted_count = 0
    new_table = []

    for record in table:
        if (
            (student_id is None or record[0] == student_id)
            and (first_name is None or record[1] == first_name)
            and (second_name is None or record[2] == second_name)
            and (age is None or record[3] == age)
            and (sex is None or record[4] == sex)
        ):
            deleted_count += 1
        else:
            new_table.append(record)

    db["tables"][db["current"]] = new_table

    return deleted_count
