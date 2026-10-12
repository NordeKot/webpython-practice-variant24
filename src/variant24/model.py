"""Тринадцать функций публичной модели слоя доступа к данным."""

from .storage import Storage


class Model:
    """Публичный интерфейс над хранилищем кортежей."""

    def __init__(self, clock=None):
        """Создать отдельное хранилище для REPL или RPC-сервера."""
        self.storage = Storage() if clock is None else Storage(clock)

    def create_entity(self, record):
        """Операция create для таблицы entity."""
        return self.storage.create("entity", record)

    def delete_entity(self, identifier):
        """Операция delete для таблицы entity."""
        return self.storage.delete("entity", identifier)

    def get_entity(self, identifier):
        """Операция get для таблицы entity."""
        return self.storage.get("entity", identifier)

    def list_entity(self):
        """Операция list для таблицы entity."""
        return self.storage.all("entity")

    def create_assignment(self, record):
        """Операция create для таблицы assignment."""
        return self.storage.create("assignment", record)

    def delete_assignment(self, identifier):
        """Операция delete для таблицы assignment."""
        return self.storage.delete("assignment", identifier)

    def get_assignment(self, identifier):
        """Операция get для таблицы assignment."""
        return self.storage.get("assignment", identifier)

    def list_assignment(self):
        """Операция list для таблицы assignment."""
        return self.storage.all("assignment")

    def create_feedback(self, record):
        """Операция create для таблицы feedback."""
        return self.storage.create("feedback", record)

    def delete_feedback(self, identifier):
        """Операция delete для таблицы feedback."""
        return self.storage.delete("feedback", identifier)

    def get_feedback(self, identifier):
        """Операция get для таблицы feedback."""
        return self.storage.get("feedback", identifier)

    def list_feedback(self):
        """Операция list для таблицы feedback."""
        return self.storage.all("feedback")

    def recent_feedback(self):
        """Проекция parameter, cache_hit, output левого соединения."""
        return self.storage.recent_feedback()
