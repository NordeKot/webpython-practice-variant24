"""Генерируемые проверки интерактивного режима и команд запуска."""

from unittest.mock import patch

from hypothesis import given, settings
from hypothesis import strategies as st

from variant24.__main__ import main
from variant24.client import RpcClient
from variant24.demo import demonstrate
from variant24.model import Model
from variant24.repl import repl
from variant24.server import serve

from .support import running_server


@given(ending=st.sampled_from(["exit", "eof"]))
def test_repl(ending):
    """Проверить успешные команды, ошибки и оба способа выхода."""
    lines = [
        '{"method":"list_entity"}',
        '{"method":"get_entity","args":[999]}',
        '{"method":"list_entity","args":[1]}',
        '{"method":"unknown"}',
        '{"method":"list_entity","args":{}}',
        '[]', '{',
    ]
    final = "exit" if ending == "exit" else EOFError()
    with patch("builtins.input", side_effect=lines + [final]):
        repl()


@given(remote=st.booleans())
@settings(max_examples=2, deadline=None)
def test_demonstration(remote):
    """Проверить демонстрацию локально и по настоящему TCP."""
    with running_server() as server:
        target = RpcClient(*server.server_address) if remote else Model()
        demonstrate(target)


@given(mode=st.sampled_from(["model", "server", "client", "demo",
                             "rpc-demo"]))
def test_main(mode):
    """Проверить маршрутизацию всех режимов командной строки."""
    argv = ["variant24", mode, "--port", "8025"]
    with patch("sys.argv", argv), patch("variant24.__main__.serve") as run:
        with patch("variant24.__main__.repl") as interactive:
            with patch("variant24.__main__.demonstrate") as demo:
                main()
                if mode == "server":
                    run.assert_called_once_with("127.0.0.1", 8025)
                elif mode in ("demo", "rpc-demo"):
                    demo.assert_called_once()
                else:
                    interactive.assert_called_once()


@given(interrupt=st.booleans())
def test_server_entry(interrupt):
    """Проверить штатное завершение и обработку Ctrl+C."""
    with patch("variant24.server.RpcServer") as factory:
        server = factory.return_value.__enter__.return_value
        if interrupt:
            server.serve_forever.side_effect = KeyboardInterrupt()
        serve(port=0)
        server.serve_forever.assert_called_once()
