"""Команды запуска модели, сервера, клиента и демонстраций."""

import argparse

from .client import RpcClient
from .demo import demonstrate
from .model import Model
from .repl import repl
from .server import DEFAULT_HOST, DEFAULT_PORT, serve


def main():
    """Выбрать режим из аргументов командной строки."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", default="model",
                        choices=["model", "server", "client", "demo",
                                 "rpc-demo"])
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    if args.mode == "server":
        serve(args.host, args.port)
        return
    remote = args.mode in ("client", "rpc-demo")
    target = RpcClient(args.host, args.port) if remote else Model()
    if args.mode in ("demo", "rpc-demo"):
        demonstrate(target)
    else:
        repl(target)


if __name__ == "__main__":
    main()
