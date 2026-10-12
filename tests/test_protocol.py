"""Проверки формата протокола также генерируются Hypothesis."""

import json
import socket
import threading

from hypothesis import given, settings
from hypothesis import strategies as st

from variant24.client import RpcClient, RpcError
from variant24.protocol import (
    MAX_BODY_SIZE,
    ProtocolError,
    encode_body,
    pack_request,
    pack_response,
    read_response,
    recv_body,
    recv_exact,
)

from .support import running_server


@given(operation=st.integers(min_value=1, max_value=13),
       args=st.lists(st.text(max_size=15), max_size=3))
def test_wire_layout(operation, args):
    """Независимо сверить смещения, размеры и little-endian байты."""
    request = pack_request(operation, args)
    body = json.dumps(args, ensure_ascii=False).encode("utf-8")
    assert request[:3] == bytes([1, operation, 0])
    assert request[3:6] == len(body).to_bytes(3, "little")
    assert request[6:] == body
    response = pack_response(operation, args)
    assert response[0] == operation
    assert response[1:5] == len(body).to_bytes(4, "little")
    assert response[5:] == body


@given(payload=st.binary(min_size=1, max_size=100),
       chunk=st.integers(min_value=1, max_value=9))
def test_fragmentation(payload, chunk):
    """Получить цельное сообщение из произвольных частей TCP."""
    left, right = socket.socketpair()
    with left, right:
        thread = threading.Thread(target=send_parts,
                                  args=(left, payload, chunk))
        thread.start()
        assert recv_exact(right, len(payload)) == payload
        thread.join(timeout=5)
        assert not thread.is_alive()


def send_parts(connection, payload, chunk):
    """Послать данные небольшими порциями и обозначить конец ввода."""
    for start in range(0, len(payload), chunk):
        connection.sendall(payload[start:start + chunk])
    connection.shutdown(socket.SHUT_WR)


@given(kind=st.sampled_from(["version", "operation", "json", "args",
                             "arity", "oversize", "short", "utf8"]))
@settings(max_examples=16, deadline=None, derandomize=True)
def test_invalid_requests(kind):
    """Сервер возвращает ошибку при разных повреждённых запросах."""
    requests = {
        "version": pack_request(4, [], version=2),
        "operation": pack_request(65535, []),
        "json": b"\x01\x04\x00\x01\x00\x00{",
        "args": pack_request(4, {}),
        "arity": pack_request(4, [1]),
        "oversize": (b"\x01\x04\x00"
                     + (MAX_BODY_SIZE + 1).to_bytes(3, "little")),
        "short": b"\x01",
        "utf8": b"\x01\x04\x00\x01\x00\x00\xff",
    }
    expected_op = 0 if kind in ("operation", "short") else 4
    with running_server() as server:
        with socket.create_connection(
                server.server_address, timeout=5) as sock:
            sock.sendall(requests[kind])
            sock.shutdown(socket.SHUT_WR)
            response = read_response(sock, expected_op)
            assert response["ok"] is False
            assert response["error"]
        assert RpcClient(*server.server_address).list_entity() == []


@given(mode=st.sampled_from(["eof", "large", "mismatch"]))
def test_protocol_errors(mode):
    """Проверить отказ при обрыве, превышении размера и чужом ответе."""
    left, right = socket.socketpair()
    with left, right:
        if mode == "mismatch":
            left.sendall(pack_response(2, []))
        left.shutdown(socket.SHUT_WR)
        try:
            if mode == "eof":
                recv_exact(right, 1)
            elif mode == "large":
                recv_body(right, MAX_BODY_SIZE + 1)
            else:
                read_response(right, 1)
        except ProtocolError:
            return
        raise AssertionError("Ожидалась ошибка протокола")


@given(extra=st.integers(min_value=1, max_value=10))
@settings(max_examples=3)
def test_encode_limit(extra):
    """Проверить лимит тела при исходящей сериализации."""
    try:
        encode_body("x" * (MAX_BODY_SIZE + extra))
    except ProtocolError:
        return
    raise AssertionError("Ожидалось ограничение размера")


@given(table=st.sampled_from(["entity", "assignment", "feedback"]))
@settings(max_examples=3, deadline=None)
def test_non_object_record(table):
    """Передать ошибочные записи через настоящее TCP-соединение."""
    with running_server() as server:
        client = RpcClient(*server.server_address)
        try:
            getattr(client, f"create_{table}")([])
        except RpcError:
            return
        raise AssertionError("Ожидалась ошибка типа записи")


@given(empty=st.just(b""))
def test_disconnected_peer(empty):
    """Обработчик не падает при ответе отключившемуся клиенту."""
    from variant24.server import Handler

    left, right = socket.socketpair()
    left.close()
    with right:
        Handler(right, ("local", 0), None)
        assert right.recv(1) == empty
