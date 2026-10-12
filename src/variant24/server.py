"""TCP RPC-сервер с общим хранилищем и журналом в stdout."""

import json
import socketserver
import threading

from .model import Model
from .operations import METHODS
from .protocol import (
    BYTE_ORDER, REQUEST_HEADER_SIZE, VERSION, ProtocolError, pack_response,
    recv_body, recv_exact,
)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8024
SOCKET_TIMEOUT = 5
UNKNOWN_OPERATION = 0


class Handler(socketserver.BaseRequestHandler):
    """Обработчик одного запроса на соединение."""

    def dispatch(self, header):
        """Проверить заголовок и вызвать функцию модели под блокировкой."""
        if header[0] != VERSION:
            raise ProtocolError("Неподдерживаемая версия")
        operation = int.from_bytes(header[1:3], BYTE_ORDER)
        if operation not in range(1, len(METHODS) + 1):
            raise ProtocolError("Неизвестная операция")
        size = int.from_bytes(header[3:6], BYTE_ORDER)
        arguments = recv_body(self.request, size)
        self.arguments = arguments
        if not isinstance(arguments, list):
            raise ProtocolError("Тело запроса должно быть массивом args")
        with self.server.lock:
            method = getattr(self.server.model, METHODS[operation - 1])
            return method(*arguments)

    def handle(self):
        """Ответить результатом либо ошибкой; записать запрос в stdout."""
        self.request.settimeout(SOCKET_TIMEOUT)
        operation = UNKNOWN_OPERATION
        self.arguments = None
        header = b""
        try:
            header = recv_exact(self.request, REQUEST_HEADER_SIZE)
            code = int.from_bytes(header[1:3], BYTE_ORDER)
            operation = code if code in range(1, len(METHODS) + 1) else 0
            result = {"ok": True, "result": self.dispatch(header)}
        except (ValueError, TypeError, OSError) as error:
            result = {"ok": False, "error": str(error)}
        print(json.dumps({"peer": self.client_address, "header": header.hex(),
                          "operation": operation, "arguments": self.arguments,
                          "response": result},
                         ensure_ascii=False), flush=True)
        try:
            self.request.sendall(pack_response(operation, result))
        except (OSError, ProtocolError):
            return


class RpcServer(socketserver.ThreadingTCPServer):
    """Потоковый сервер; операции атомарны относительно общего хранилища."""

    allow_reuse_address = True
    daemon_threads = True
    block_on_close = True

    def __init__(self, address=(DEFAULT_HOST, DEFAULT_PORT), clock=None):
        """Создать сокет и модель; порт 0 выбирает свободный порт."""
        self.model = Model(clock)
        self.lock = threading.RLock()
        super().__init__(address, Handler)


def serve(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Запустить сервер до Ctrl+C; после остановки данные теряются."""
    with RpcServer((host, port)) as server:
        print(f"RPC listening on {host}:{port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Сервер остановлен")
