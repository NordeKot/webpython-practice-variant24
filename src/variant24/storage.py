"""Хранилище кортежей без сохранения записей на диск."""

import time

from .schema import REFERENCES, SCHEMAS, WINDOW_SECONDS


class ModelError(ValueError):
    """Ошибка данных: поля, типы, ключи или связи."""


class Storage:
    """Изолированное хранилище; clock возвращает Unix-время в секундах."""

    def __init__(self, clock=time.time):
        """Создать пустые таблицы с независимым временем для тестирования."""
        self.tables = {name: {} for name in SCHEMAS}
        self.clock = clock

    def validate(self, table, record):
        """Проверить полный набор полей и точные типы, включая запрет bool."""
        schema = SCHEMAS[table]
        if not isinstance(record, dict) or record.keys() != schema.keys():
            raise ModelError("Нужен объект с точным набором полей таблицы")
        for field, expected in schema.items():
            if type(record[field]) is not expected:
                raise ModelError(f"Неверный тип поля {field}")
        if table in REFERENCES:
            field, parent = REFERENCES[table]
            self.get(parent, record[field])

    def create(self, table, record):
        """Создать кортеж с заданным пользователем уникальным ключом."""
        self.validate(table, record)
        identifier = record["identifier"]
        if identifier in self.tables[table]:
            raise ModelError("Идентификатор уже существует")
        row = tuple(record[field] for field in SCHEMAS[table])
        self.tables[table][identifier] = row
        return row

    def get(self, table, identifier):
        """Получить запись; отсутствующий или неверный ключ является ошибкой."""
        if type(identifier) is not int:
            raise ModelError("Идентификатор должен иметь тип int")
        if identifier not in self.tables[table]:
            raise ModelError("Запись не найдена")
        return self.tables[table][identifier]

    def delete(self, table, identifier):
        """Удалить запись без зависимых записей; каскадного удаления нет."""
        self.get(table, identifier)
        for child, (field, parent) in REFERENCES.items():
            if parent == table and self.is_referenced(child, field, identifier):
                raise ModelError("На запись ссылаются другие записи")
        del self.tables[table][identifier]
        return None

    def is_referenced(self, table, field, identifier):
        """Проверить внешний ключ по всем строкам дочерней таблицы."""
        index = tuple(SCHEMAS[table]).index(field)
        return any(row[index] == identifier
                   for row in self.tables[table].values())

    def all(self, table):
        """Вернуть список кортежей, отсортированный по идентификатору."""
        return [row for _, row in sorted(self.tables[table].items())]

    def recent_feedback(self):
        """Выполнить DISTINCT-проекцию левого соединения за пять минут."""
        cutoff = self.clock() - WINDOW_SECONDS
        result = set()
        feedback = self.all("feedback")
        for assignment in self.all("assignment"):
            matches = [row for row in feedback
                       if row[5] == assignment[0] and row[1] > cutoff]
            if matches:
                result.update((assignment[2], row[6], row[2])
                              for row in matches)
            else:
                result.add((assignment[2], None, None))
        return sorted(result, key=repr)
