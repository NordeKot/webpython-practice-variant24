"""Независимая упрощённая модель MBT: словари вместо кортежей."""

NOW = 1_800_000_000
WINDOW = 300
FIELDS = {
    "entity": ("identifier", "created", "ip", "locale", "platform"),
    "assignment": ("identifier", "created", "parameter", "entity",
                   "tags", "stage", "triggered"),
    "feedback": ("identifier", "created", "output", "stage", "exception",
                 "assignment", "cache_hit", "duration"),
}
INTEGER_FIELDS = {
    "identifier", "created", "entity", "triggered", "assignment",
    "cache_hit", "duration",
}
PARENTS = {"assignment": "entity", "feedback": "assignment"}


class ReferenceError(ValueError):
    """Ожидаемая ошибка независимой модели."""


class Reference:
    """Эталонные записи представлены словарями, без кода сервера."""

    def __init__(self):
        """Создать пустое эталонное состояние."""
        self.tables = {name: {} for name in FIELDS}

    def create(self, table, row):
        """Проверить запись и добавить её копию в эталон."""
        if not isinstance(row, dict) or set(row) != set(FIELDS[table]):
            raise ReferenceError()
        for field, value in row.items():
            expected = int if field in INTEGER_FIELDS else str
            if type(value) is not expected:
                raise ReferenceError()
        identifier = row["identifier"]
        if identifier in self.tables[table]:
            raise ReferenceError()
        if table in PARENTS:
            parent = PARENTS[table]
            self.get(parent, row[parent])
        self.tables[table][identifier] = row.copy()
        return self.as_list(table, row)

    def get(self, table, identifier):
        """Получить запись или ожидаемую ошибку."""
        if type(identifier) is not int or identifier not in self.tables[table]:
            raise ReferenceError()
        return self.as_list(table, self.tables[table][identifier])

    def delete(self, table, identifier):
        """Удалить запись только при отсутствии ссылок на неё."""
        self.get(table, identifier)
        for child, parent in PARENTS.items():
            if parent == table:
                for row in self.tables[child].values():
                    if row[parent] == identifier:
                        raise ReferenceError()
        del self.tables[table][identifier]
        return None

    def as_list(self, table, row):
        """Представить эталонную запись в порядке ER-полей."""
        return [row[field] for field in FIELDS[table]]

    def list_rows(self, table):
        """Получить все записи в порядке ключей."""
        return [self.as_list(table, self.tables[table][key])
                for key in sorted(self.tables[table])]

    def query(self):
        """Независимая реализация LEFT JOIN, фильтра и DISTINCT."""
        result = []
        for assignment in self.tables["assignment"].values():
            found = False
            for feedback in self.tables["feedback"].values():
                same = feedback["assignment"] == assignment["identifier"]
                recent = feedback["created"] > NOW - WINDOW
                if same and recent:
                    found = True
                    row = [assignment["parameter"], feedback["cache_hit"],
                           feedback["output"]]
                    if row not in result:
                        result.append(row)
            missing = [assignment["parameter"], None, None]
            if not found and missing not in result:
                result.append(missing)
        return sorted(result, key=lambda row: repr(tuple(row)))

    def call(self, method, arguments):
        """Выполнить публичную операцию эталонной модели."""
        if method == "recent_feedback":
            return self.query()
        operation, table = method.split("_", maxsplit=1)
        if operation == "list":
            return self.list_rows(table)
        return getattr(self, operation)(table, *arguments)


def record(table, identifier, parent, offset, text):
    """Построить данные из стратегии Hypothesis без схемы сервера."""
    rows = {
        "entity": dict(identifier=identifier, created=NOW + offset,
                       ip=text, locale=text, platform=text),
        "assignment": dict(identifier=identifier, created=NOW + offset,
                           parameter=text, entity=parent, tags=text,
                           stage=text, triggered=NOW),
        "feedback": dict(identifier=identifier, created=NOW + offset,
                         output=text, stage=text, exception=text,
                         assignment=parent, cache_hit=identifier % 2,
                         duration=identifier),
    }
    return rows[table]
