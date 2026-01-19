## Latency comparisons

- [urllib3 (sync)](#urllib3)
- [aiohttp (async)](#aiohttp)
- [httpx (async)](#httpx)
- [rnet (async)](#rnet)
- [niquests (async)](#niquests)
- [ry (async)](#ry)

In graphs `pyreqwest (st)` uses single-threaded and `pyreqwest (mt)` multi-threaded [runtime](./performance.md#async-runtime).

### Compared to [urllib3](https://github.com/urllib3/urllib3) (sync) <a name="urllib3" id="urllib3"></a>

<p align="center">
    <img width="1200" alt="result" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_urllib3.png" />
</p>

### Compared to [aiohttp](https://github.com/aio-libs/aiohttp) (async) <a name="aiohttp" id="aiohttp"></a>

<p align="center">
    <img width="1200" alt="result" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_aiohttp.png" />
</p>

### Compared to [httpx](https://github.com/encode/httpx) (async) <a name="httpx" id="httpx"></a>

<p align="center">
    <img width="1200" alt="result" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_httpx.png" />
</p>

### Compared to [rnet](https://github.com/0x676e67/rnet) (async) <a name="rnet" id="rnet"></a>

<p align="center">
    <img width="1200" alt="result" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_rnet.png" />
</p>

### Compared to [niquests](https://github.com/jawah/niquests) (async) <a name="niquests" id="niquests"></a>

<p align="center">
    <img width="1200" alt="result" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_niquests.png" />
</p>

### Compared to [ry](https://github.com/jessekrubin/ry) (async) <a name="ry" id="ry"></a>

<p align="center">
    <img width="1200" alt="result" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_ry.png" />
</p>

---

## GC pressure

| Library (mode)    | Total Collections | Total Collected |
|-------------------|-------------------|-----------------|
| pyreqwest (async) | 22                | 0               |
| pyreqwest (sync)  | 25                | 0               |
| ry (async)        | 39                | 0               |
| rnet (async)      | 40                | 0               |
| aiohttp (async)   | 377               | 3978            |
| urllib3 (sync)    | 427               | 821689          |
| httpx (async)     | 772               | 1347560         |
| niquests (async)  | 1260              | 2667198         |

---

## Benchmark

```bash
make bench
```
Benchmarks run against embedded server to minimize any network effects on latency measurements. Python 3.14 was used.
Connections use HTTP/1.1 with TLS.
Benchmarks were run on Apple M3 Max machine with 36GB RAM (OS 15.7.3).
