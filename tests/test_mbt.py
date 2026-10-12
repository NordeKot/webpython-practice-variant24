"""Сгенерированные Hypothesis сценарии всех 13 методов RPC."""

from hypothesis import settings, strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine, initialize, invariant, rule,
)

from variant24.client import RpcClient, RpcError

from .reference import FIELDS, Reference, ReferenceError, record
from .support import running_server

TABLES = tuple(FIELDS)
TEXT = st.text(max_size=12)
KEYS = st.integers(min_value=-3, max_value=5)
OFFSETS = st.sampled_from([-301, -300, -299, 0, 300])


class RpcMachine(RuleBasedStateMachine):
    """Сравнить последовательности реальных TCP-вызовов с эталоном."""

    def __init__(self):
        """Поднять новый сервер для каждого сгенерированного сценария."""
        super().__init__()
        self.context = running_server()
        self.server = self.context.__enter__()
        self.client = RpcClient(*self.server.server_address)
        self.reference = Reference()
        self.serial = 1000

    def compare(self, method, *arguments):
        """Сравнить результат или категорию ошибки после одного вызова."""
        try:
            expected = self.reference.call(method, arguments)
        except ReferenceError:
            try:
                getattr(self.client, method)(*arguments)
            except RpcError:
                return
            raise AssertionError(f"RPC должен вернуть ошибку: {method}")
        actual = getattr(self.client, method)(*arguments)
        assert actual == expected

    @initialize(text=TEXT, key=KEYS)
    def full_lifecycle(self, text, key):
        """В каждом сценарии вызвать все методы с генерируемыми данными."""
        for table in TABLES:
            row = record(table, key, key, 0, text)
            self.compare(f"create_{table}", row)
            self.compare(f"get_{table}", key)
            self.compare(f"list_{table}")
            self.compare(f"create_{table}", row)
        self.compare("recent_feedback")
        self.compare("delete_entity", key)
        self.compare("delete_assignment", key)
        for table in reversed(TABLES):
            self.compare(f"delete_{table}", key)
            self.compare(f"get_{table}", key)
            self.compare(f"delete_{table}", key)

    @rule(table=st.sampled_from(TABLES), key=KEYS, parent=KEYS,
          offset=OFFSETS, text=TEXT)
    def create(self, table, key, parent, offset, text):
        """Создавать записи с существующими или отсутствующими ссылками."""
        self.compare(f"create_{table}",
                     record(table, key, parent, offset, text))

    @rule(table=st.sampled_from(TABLES), key=KEYS,
          action=st.sampled_from(["get", "delete"]))
    def access(self, table, key, action):
        """Читать и удалять разные записи текущего состояния."""
        self.compare(f"{action}_{table}", key)

    @rule(table=st.sampled_from(TABLES), key=KEYS, text=TEXT,
          kind=st.sampled_from(["missing", "extra", "type", "boolean"]))
    def invalid_record(self, table, key, text, kind):
        """Проверять неполные записи, лишние поля и неправильные типы."""
        row = record(table, key, key, 0, text)
        if kind == "missing":
            del row["created"]
        elif kind == "extra":
            row["extra"] = text
        elif kind == "type":
            row["created"] = text
        else:
            row["identifier"] = True
        self.compare(f"create_{table}", row)

    @rule(table=st.sampled_from(TABLES), key=st.one_of(TEXT, st.booleans()))
    def invalid_key(self, table, key):
        """Запретить строковые и логические идентификаторы."""
        self.compare(f"get_{table}", key)
        self.compare(f"delete_{table}", key)

    @rule(text=TEXT, offset=OFFSETS)
    def join_scenario(self, text, offset):
        """Проверить границу пяти минут, LEFT JOIN и повтор проекции."""
        self.serial += 10
        key = self.serial
        self.compare("create_entity", record("entity", key, key, 0, text))
        self.compare("create_assignment",
                     record("assignment", key, key, 0, text))
        self.compare("recent_feedback")
        first = record("feedback", key, key, offset, text)
        second = dict(first, identifier=key + 1)
        self.compare("create_feedback", first)
        self.compare("create_feedback", second)
        self.compare("recent_feedback")
        self.compare("delete_feedback", key)
        self.compare("delete_feedback", key + 1)
        self.compare("delete_assignment", key)
        self.compare("delete_entity", key)

    @invariant()
    def snapshots(self):
        """После каждого шага проверять таблицы и результат соединения."""
        for table in TABLES:
            self.compare(f"list_{table}")
        self.compare("recent_feedback")
        for rows in self.server.model.storage.tables.values():
            assert all(isinstance(row, tuple) for row in rows.values())

    def teardown(self):
        """Остановить сервер и закрыть сокеты после каждого сценария."""
        self.context.__exit__(None, None, None)


TestRpcMachine = RpcMachine.TestCase
TestRpcMachine.settings = settings(
    max_examples=40, stateful_step_count=35, deadline=None, derandomize=True,
)
