"""Runtime configuration. See Tokio runtime documentation for details about config parameters."""

from pyreqwest._pyreqwest.runtime import (
    runtime_blocking_thread_keep_alive,
    runtime_max_blocking_threads,
    runtime_multithreaded_default,
    runtime_worker_threads,
)

__all__ = [
    "runtime_multithreaded_default",
    "runtime_worker_threads",
    "runtime_max_blocking_threads",
    "runtime_blocking_thread_keep_alive",
]
