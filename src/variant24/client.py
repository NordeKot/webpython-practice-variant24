"""Клиент с теми же тринадцатью именами методов, что и у модели."""

import socket

from .operations import OP_CODES
from .protocol import pack_request, read_response
from .server import DEFAULT_HOST, DEFAULT_PORT, SOCKET_TIMEOUT


class RpcError(ValueError):
    """Ошибка, полученная от RPC-сервера."""


class RpcClient:
    """Один TCP-запрос на вызов; JSON-кортежи приходят как списки."""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """Сохранить адрес сервера без установления соединения."""
        self.address = (host, port)

    def call(self, name, *arguments):
        """Передать аргументы по TCP и вернуть результат или RpcError."""
        operation = OP_CODES[name]
        with socket.create_connection(self.address, SOCKET_TIMEOUT) as sock:
            sock.sendall(pack_request(operation, arguments))
            response = read_response(sock, operation)
        if not response["ok"]:
            raise RpcError(response["error"])
        return response["result"]

    def create_entity(self, record):
        """Удалённая операция create для entity."""
        return self.call("create_entity", record)

    def delete_entity(self, identifier):
        """Удалённая операция delete для entity."""
        return self.call("delete_entity", identifier)

    def get_entity(self, identifier):
        """Удалённая операция get для entity."""
        return self.call("get_entity", identifier)

    def list_entity(self):
        """Удалённая операция list для entity."""
        return self.call("list_entity")

    def create_assignment(self, record):
        """Удалённая операция create для assignment."""
        return self.call("create_assignment", record)

    def delete_assignment(self, identifier):
        """Удалённая операция delete для assignment."""
        return self.call("delete_assignment", identifier)

    def get_assignment(self, identifier):
        """Удалённая операция get для assignment."""
        return self.call("get_assignment", identifier)

    def list_assignment(self):
        """Удалённая операция list для assignment."""
        return self.call("list_assignment")

    def create_feedback(self, record):
        """Удалённая операция create для feedback."""
        return self.call("create_feedback", record)

    def delete_feedback(self, identifier):
        """Удалённая операция delete для feedback."""
        return self.call("delete_feedback", identifier)

    def get_feedback(self, identifier):
        """Удалённая операция get для feedback."""
        return self.call("get_feedback", identifier)

    def list_feedback(self):
        """Удалённая операция list для feedback."""
        return self.call("list_feedback")

    def recent_feedback(self):
        """Удалённое левое соединение со свежими отзывами."""
        return self.call("recent_feedback")
