"""Управление настоящим TCP-сервером в тестах."""

import threading
from contextlib import contextmanager

from variant24.server import RpcServer

from .reference import NOW


@contextmanager
def running_server():
    """Создать изолированный сервер с фиксированным тестовым временем."""
    with RpcServer(("127.0.0.1", 0), clock=lambda: NOW) as server:
        thread = threading.Thread(
            target=server.serve_forever, kwargs={"poll_interval": 0.01},
            daemon=True,
        )
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive()
