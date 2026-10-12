"""Стабильные коды тринадцати публичных операций."""

METHODS = (
    "create_entity", "delete_entity", "get_entity", "list_entity",
    "create_assignment", "delete_assignment", "get_assignment",
    "list_assignment", "create_feedback", "delete_feedback",
    "get_feedback", "list_feedback", "recent_feedback",
)
OP_CODES = {name: index for index, name in enumerate(METHODS, start=1)}
