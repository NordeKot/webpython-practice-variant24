# Практическая работа №1, вариант 24

Python 3.10+. Прототип с данными только в оперативной памяти.
Схема: Entity → Assignment → Feedback. Записи хранятся кортежами
в порядке полей ER-диаграммы (см. src/variant24/schema.py).

## Этап 1

Запуск: `run.bat` (Windows) или `./run.sh` (Linux/macOS).
Команды REPL содержат `method` и массив `args`.
Пример: `{"method":"list_entity","args":[]}`. Выход: `exit`.
Каждая таблица имеет create, delete, get, list; recent_feedback
возвращает parameter, cache_hit, output для LEFT JOIN с отзывами
строго новее now - 300 секунд. При отсутствии отзыва: null, null.
Повторы проекции удаляются согласно реляционной алгебре.
Идентификаторы задаёт пользователь. created и triggered: Unix-секунды.
Удаление родителя с зависимыми строками запрещено.
