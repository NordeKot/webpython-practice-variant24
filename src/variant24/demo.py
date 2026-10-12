"""Демонстрация всех тринадцати методов и обработки ошибок."""

import json
import time

from .repl import execute


def commands():
    """Подготовить JSON-команды, одинаковые для модели и клиента."""
    now = int(time.time())
    entity = dict(identifier=1, created=now, ip="127.0.0.1",
                  locale="ru", platform="Windows")
    assignment = dict(identifier=10, created=now, parameter="example",
                      entity=1, tags="demo", stage="new", triggered=now)
    feedback = dict(identifier=100, created=now, output="done", stage="ok",
                    exception="", assignment=10, cache_hit=1, duration=12)
    return [
        ("create_entity", [entity]), ("get_entity", [1]),
        ("list_entity", []), ("create_entity", [entity]),
        ("create_assignment", [assignment]), ("get_assignment", [10]),
        ("list_assignment", []), ("recent_feedback", []),
        ("create_feedback", [feedback]), ("get_feedback", [100]),
        ("list_feedback", []), ("recent_feedback", []),
        ("delete_entity", [1]), ("delete_assignment", [10]),
        ("delete_feedback", [100]), ("delete_assignment", [10]),
        ("delete_entity", [1]), ("get_entity", [1]),
        ("list_entity", []), ("list_assignment", []),
        ("list_feedback", []), ("recent_feedback", []),
    ]


def demonstrate(target):
    """Вывести все команды и результаты, включая ожидаемые ошибки."""
    for method, args in commands():
        text = json.dumps({"method": method, "args": args},
                          ensure_ascii=False)
        print(f"> {text}")
        try:
            print(json.dumps(execute(target, text), ensure_ascii=False))
        except ValueError as error:
            print(f"Ожидаемая ошибка: {error}")
