## Latency

### Compared to [urllib3](https://github.com/urllib3/urllib3) (sync)

<p align="center">
    <img width="1200" alt="urllib3" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_urllib3.png" />
</p>

### Compared to [aiohttp](https://github.com/aio-libs/aiohttp) (async)

<p align="center">
    <img width="1200" alt="aiohttp" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_aiohttp.png" />
</p>

### Compared to [httpx](https://github.com/encode/httpx) (async)

<p align="center">
    <img width="1200" alt="httpx" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_httpx.png" />
</p>

### Compared to [rnet](https://github.com/0x676e67/rnet) (async)

<p align="center">
    <img width="1200" alt="rnet" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_rnet.png" />
</p>

<!-- TODO(Markus): UNCOMMENT WHEN RUN -->
<!--
### Compared to [ry](https://github.com/jessekrubin/ry) (async)

<p align="center">
    <img width="1200" alt="rnet" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_ry.png" />
</p>
-->


### Compared to [niquests](https://github.com/jawah/niquests) (async)

<p align="center">
    <img width="1200" alt="rnet" src="https://raw.githubusercontent.com/MarkusSintonen/pyreqwest/refs/heads/main/tests/bench/benchmark_niquests.png" />
</p>

---

## GC pressure

| Library (mode)    | Total Collections | Total Collected |
|-------------------|-------------------|-----------------|
| pyreqwest (async) | 22                | 0               |
| pyreqwest (sync)  | 25                | 0               |
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
Benchmarks run against (concurrency limited) embedded server to minimize any network effects on latency measurements.
Connections use HTTP/1.1 with TLS.
Benchmarks were run on Apple M3 Max machine with 36GB RAM (OS 15.7.3).
