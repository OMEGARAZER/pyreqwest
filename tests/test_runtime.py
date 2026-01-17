import multiprocessing
from datetime import timedelta
from multiprocessing import Queue

import pytest

from tests.servers.server_subprocess import SubprocessServer


def config_test_isolated(queue: Queue[str | BaseException], url: str, set_default: bool) -> None:
    try:
        from pyreqwest.client import SyncClientBuilder
        from pyreqwest.runtime import (
            runtime_blocking_thread_keep_alive,
            runtime_max_blocking_threads,
            runtime_multithreaded_default,
            runtime_worker_threads,
        )

        runtime_worker_threads(2)  # No effect yet
        runtime_max_blocking_threads(64)
        runtime_blocking_thread_keep_alive(timedelta(seconds=10))

        with SyncClientBuilder().runtime_multithreaded(False).build() as client:
            assert client.get(url).build().send().status == 200
        with SyncClientBuilder().build() as client:  # Default does not use MT
            assert client.get(url).build().send().status == 200

        runtime_worker_threads(3)  # Can still change, MT not used
        runtime_max_blocking_threads(128)
        runtime_blocking_thread_keep_alive(timedelta(seconds=20))

        if set_default:
            runtime_multithreaded_default(True)
            with SyncClientBuilder().build() as client:
                assert client.get(url).build().send().status == 200
        else:
            with SyncClientBuilder().runtime_multithreaded(True).build() as client:
                assert client.get(url).build().send().status == 200

        runtime_worker_threads(3)  # Same value used
        runtime_max_blocking_threads(128)
        runtime_blocking_thread_keep_alive(timedelta(seconds=20))

        msg = "Multi-threaded runtime config can not be changed after the runtime has been initialized"
        with pytest.raises(RuntimeError, match=msg):
            runtime_worker_threads(4)  # Can not change anymore as MT was initialized
        with pytest.raises(RuntimeError, match=msg):
            runtime_max_blocking_threads(256)
        with pytest.raises(RuntimeError, match=msg):
            runtime_blocking_thread_keep_alive(timedelta(seconds=30))

        with SyncClientBuilder().runtime_multithreaded(True).build() as client:
            assert client.get(url).build().send().status == 200

        queue.put("OK")
    except BaseException as e:
        queue.put(repr(e))
        raise


@pytest.mark.parametrize("set_default", [False, True])
def test_config_isolated(echo_server: SubprocessServer, set_default: bool) -> None:
    queue: Queue[str | BaseException] = Queue()
    process = multiprocessing.Process(target=config_test_isolated, args=(queue, str(echo_server.url), set_default))
    process.start()
    process.join(timeout=20)
    assert queue.get(timeout=20) == "OK"
    assert process.exitcode == 0
