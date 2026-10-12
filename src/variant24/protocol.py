"""Бинарное обрамление JSON согласно таблице 24, little-endian."""

import json

VERSION = 1
REQUEST_HEADER_SIZE = 6
RESPONSE_HEADER_SIZE = 5
MAX_BODY_SIZE = 1024 * 1024
BYTE_ORDER = "little"


class ProtocolError(ValueError):
    """Некорректное или оборванное сообщение протокола."""


def encode_body(value):
    """Сериализовать JSON в UTF-8 и ограничить размер сообщения."""
    body = json.dumps(value, ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_BODY_SIZE:
        raise ProtocolError("Слишком большое тело сообщения")
    return body


def recv_exact(connection, size):
    """Читать ровно size байтов, учитывая фрагментацию TCP."""
    result = bytearray()
    while len(result) < size:
        part = connection.recv(size - len(result))
        if not part:
            raise ProtocolError("Соединение оборвано")
        result.extend(part)
    return bytes(result)


def recv_body(connection, size):
    """Проверить размер, затем декодировать JSON из полного тела."""
    if size > MAX_BODY_SIZE:
        raise ProtocolError("Слишком большое тело сообщения")
    return json.loads(recv_exact(connection, size).decode("utf-8"))


def pack_request(operation, arguments, version=VERSION):
    """Запрос: версия 1, операция 2, длина 3 байта, затем JSON."""
    body = encode_body(arguments)
    return (bytes([version]) + operation.to_bytes(2, BYTE_ORDER)
            + len(body).to_bytes(3, BYTE_ORDER) + body)


def pack_response(operation, result):
    """Ответ: операция 1, длина 4 байта, затем JSON."""
    body = encode_body(result)
    return (bytes([operation]) + len(body).to_bytes(4, BYTE_ORDER)
            + body)


def read_response(connection, operation):
    """Прочитать ответ и сверить его код операции с запросом."""
    header = recv_exact(connection, RESPONSE_HEADER_SIZE)
    if header[0] != operation:
        raise ProtocolError("Код операции ответа не совпадает")
    return recv_body(connection, int.from_bytes(header[1:], BYTE_ORDER))
