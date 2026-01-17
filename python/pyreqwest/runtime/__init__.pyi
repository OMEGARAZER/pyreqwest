from datetime import timedelta

def runtime_multithreaded_default(enable: bool | None) -> None:
    """Enable to use multithreaded runtime by default. None uses default behavior which is to use single-threaded
    runtime.
    """

def runtime_worker_threads(threads: int | None) -> None:
    """Set the number of worker threads for the multithreaded runtime. None uses default Tokio behavior which is the
    number of cores available to the system.

    Should be configured at startup. Can not be changed after multithreaded runtime has been initialized.
    """

def runtime_max_blocking_threads(threads: int | None) -> None:
    """Set the maximum number of blocking threads for the multithreaded runtime. None uses default Tokio behavior.

    Should be configured at startup. Can not be changed after multithreaded runtime has been initialized.
    """

def runtime_blocking_thread_keep_alive(seconds: timedelta | None) -> None:
    """Set the keep-alive time for blocking threads in the multithreaded runtime. None uses default Tokio behavior.

    Should be configured at startup. Can not be changed after multithreaded runtime has been initialized.
    """
