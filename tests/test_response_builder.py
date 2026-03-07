import gc
import weakref
from collections.abc import AsyncGenerator, AsyncIterator, Iterator
from typing import Any, assert_never

import pytest
from pyreqwest.response import Response, ResponseBuilder, SyncResponse
from pyreqwest.types import ExtensionsType


@pytest.mark.parametrize("sync", [False, True])
async def test_default(sync: bool):
    builder = ResponseBuilder()
    resp = builder.build_sync() if sync else await builder.build()
    assert resp.status == 200
    assert resp.headers == {}
    assert resp.extensions == {}
    assert resp.version == "HTTP/1.1"
    if isinstance(resp, Response):
        assert (await resp.bytes()) == b""
    elif isinstance(resp, SyncResponse):
        assert resp.bytes() == b""
    else:
        assert_never(resp)


@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("status", [200, 400])
async def test_status(sync: bool, status: int):
    builder = ResponseBuilder().status(status)
    resp = builder.build_sync() if sync else await builder.build()
    assert resp.status == status


@pytest.mark.parametrize("sync", [False, True])
async def test_headers(sync: bool):
    builder = (
        ResponseBuilder()
        .headers([("X-Test", "Value0")])
        .headers([("X-Test", "Value1"), ("X-Test", "Value2")])
        .header("X-Test", "Value3")
        .header("X-Test2", "Value4")
        .header("X-Test2", "Value5")
    )
    resp = builder.build_sync() if sync else await builder.build()
    assert resp.headers["X-Test"] == "Value1"
    assert resp.headers.getall("X-Test") == ["Value1", "Value2", "Value3"]
    assert resp.headers.getall("X-Test2") == ["Value4", "Value5"]


async def test_body():
    resp = await ResponseBuilder().body_json({"a": 1}).build()
    assert await resp.bytes() == b'{"a":1}'
    resp = await ResponseBuilder().body_text("foo").build()
    assert await resp.bytes() == b"foo"
    resp = await ResponseBuilder().body_bytes(b"bar").build()
    assert await resp.bytes() == b"bar"


def test_body_json__sync():
    resp = ResponseBuilder().body_json({"a": 1}).build_sync()
    assert resp.bytes() == b'{"a":1}'
    resp = ResponseBuilder().body_text("foo").build_sync()
    assert resp.bytes() == b"foo"
    resp = ResponseBuilder().body_bytes(b"bar").build_sync()
    assert resp.bytes() == b"bar"


async def test_body_stream():
    async def stream() -> AsyncIterator[bytes]:
        yield b"test1 "
        yield b"test2"

    resp = await ResponseBuilder().body_stream(stream()).build()
    assert await resp.bytes() == b"test1 test2"


def test_body_stream__sync():
    def stream() -> Iterator[bytes]:
        yield b"test1 "
        yield b"test2"

    resp = ResponseBuilder().body_stream(stream()).build_sync()
    assert resp.bytes() == b"test1 test2"


@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("extensions", [{}, {"a": 1}, [("a", 1), ("b", 2)], [("a", 1), ("a", 2)]])
async def test_extensions(sync: bool, extensions: ExtensionsType):
    builder = ResponseBuilder().extensions(extensions)
    resp = builder.build_sync() if sync else await builder.build()
    assert resp.extensions == dict(extensions)


@pytest.mark.parametrize("sync", [False, True])
@pytest.mark.parametrize("version", ["HTTP/1.1", "HTTP/2.0"])
async def test_version(sync: bool, version: str):
    builder = ResponseBuilder().version(version)
    resp = builder.build_sync() if sync else await builder.build()
    assert resp.version == version


async def sync_no_async_mix() -> None:
    async def stream() -> AsyncIterator[bytes]:
        pytest.fail("Should not be called")
        yield b""

    builder = ResponseBuilder().body_stream(stream())
    with pytest.raises(ValueError, match="Cannot use async iterator in a blocking context"):
        builder.build_sync()


def test_response_builder__circular_reference_collected() -> None:
    # Check the GC support via __traverse__ and __clear__
    ref: weakref.ReferenceType[Any] | None = None

    def check() -> None:
        nonlocal ref

        class StreamHandler:
            def __init__(self) -> None:
                self.builder: ResponseBuilder | None = None

            def __aiter__(self) -> AsyncGenerator[bytes]:
                async def gen() -> AsyncGenerator[bytes]:
                    yield b"test"

                return gen()

        stream = StreamHandler()
        resp = ResponseBuilder().body_stream(stream)
        stream.builder = resp
        ref = weakref.ref(stream)

    check()
    gc.collect()
    assert ref is not None and ref() is None
