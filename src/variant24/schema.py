"""Поля кортежей в порядке ER-диаграммы варианта 24."""

SCHEMAS = {
    "entity": {
        "identifier": int, "created": int, "ip": str,
        "locale": str, "platform": str,
    },
    "assignment": {
        "identifier": int, "created": int, "parameter": str,
        "entity": int, "tags": str, "stage": str, "triggered": int,
    },
    "feedback": {
        "identifier": int, "created": int, "output": str,
        "stage": str, "exception": str, "assignment": int,
        "cache_hit": int, "duration": int,
    },
}
REFERENCES = {"assignment": ("entity", "entity"),
              "feedback": ("assignment", "assignment")}
WINDOW_SECONDS = 5 * 60
