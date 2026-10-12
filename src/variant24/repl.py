"""Интерактивный режим: одна JSON-команда на строку, без eval."""

import json

from .model import Model
from .operations import METHODS
from .storage import ModelError


HELP = 'Формат: {"method": "list_entity", "args": []}; выход: exit'


def execute(target, text):
    """Разобрать и исполнить одну команду публичного интерфейса."""
    request = json.loads(text)
    if not isinstance(request, dict):
        raise ModelError("Команда должна быть объектом JSON")
    name = request.get("method")
    if name not in METHODS:
        raise ModelError("Неизвестный метод")
    args = request.get("args", [])
    if not isinstance(args, list):
        raise ModelError("args должен быть массивом")
    return getattr(target, name)(*args)


def repl(target=None):
    """Читать команды до exit или конца ввода и показывать ошибки."""
    target = target or Model()
    print(HELP)
    while True:
        try:
            text = input("> ").strip()
            if text == "exit":
                return
            result = execute(target, text)
            print(json.dumps(result, ensure_ascii=False))
        except EOFError:
            return
        except (ValueError, TypeError, OSError) as error:
            print(f"Ошибка: {error}")
