import asyncio
import os
import platform
import time
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TypeVar

import docker
from docker.models.containers import Container

IS_CI = os.environ.get("CI") is not None
IS_OSX = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

T = TypeVar("T")


@asynccontextmanager
async def docker_container(
    image: str, name: str, port: int = 8080, env: dict[str, str] | None = None
) -> AsyncGenerator[int, None]:
    client = docker.from_env()

    for container in client.containers.list(filters={"name": name}, all=True):
        container.remove(v=True, force=True)  # Remove existing

    container = client.containers.run(
        image, name=name, ports={f"{port}/tcp": None}, environment=env, detach=True, remove=True
    )
    assert isinstance(container, Container)

    async def container_host_port() -> int:
        container.reload()
        host_port = (container.ports.get(f"{port}/tcp") or [{}])[0].get("HostPort")
        assert host_port
        return int(host_port)

    try:
        yield await wait_for(container_host_port)
    finally:
        container.remove(v=True, force=True)


@contextmanager
def temp_file(content: bytes, suffix: str = "") -> Generator[Path, None, None]:
    """Temp file that works on windows too with subprocesses."""
    tmp = NamedTemporaryFile(suffix=suffix, delete=False)  # noqa: SIM115
    path = Path(tmp.name)
    try:
        tmp.write(content)
        tmp.flush()
        tmp.close()
        yield path
    finally:
        path.unlink()


async def wait_for(fn: Callable[[], Awaitable[T]], timeout: timedelta = timedelta(seconds=10)) -> T:
    deadline = time.monotonic() + timeout.total_seconds()
    while True:
        try:
            return await fn()
        except Exception as exc:
            if time.monotonic() > deadline:
                print(exc)
                raise
            await asyncio.sleep(0.1)
