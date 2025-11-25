"""
ابزار تست کارایی (Load / Stress) برای بک‌اند FastAPI.

اجرا:
    python -m tests.performance.run_performance_tests --username admin --password Pass123!
"""

from __future__ import annotations

import argparse
import asyncio
import os
import random
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

import httpx


DEFAULT_ENDPOINTS: list[dict[str, Any]] = [
    {"method": "GET", "path": "/api/tickets?page=1&page_size=20"},
    {"method": "GET", "path": "/api/reports/overview"},
    {"method": "GET", "path": "/api/reports/by-priority"},
    {"method": "GET", "path": "/api/branches"},
    {"method": "GET", "path": "/api/departments?page_size=100"},
    {"method": "GET", "path": "/api/sla"},
    {"method": "GET", "path": "/api/custom-fields"},
]


@dataclass
class RequestResult:
    latency_ms: float | None
    ok: bool
    status_code: int | None
    error: str | None = None
    endpoint: str | None = None


@dataclass
class TestStats:
    title: str
    results: list[RequestResult] = field(default_factory=list)

    @property
    def successes(self) -> list[RequestResult]:
        return [r for r in self.results if r.ok]

    @property
    def failures(self) -> list[RequestResult]:
        return [r for r in self.results if not r.ok]

    def summary(self) -> dict[str, Any]:
        latencies = [r.latency_ms for r in self.successes if r.latency_ms is not None]
        return {
            "title": self.title,
            "total_requests": len(self.results),
            "success_count": len(self.successes),
            "failure_count": len(self.failures),
            "avg_ms": round(statistics.mean(latencies), 2) if latencies else None,
            "p95_ms": round(percentile(latencies, 95), 2) if latencies else None,
            "max_ms": round(max(latencies), 2) if latencies else None,
            "error_samples": [r.error for r in self.failures[:5]],
        }


def percentile(data: Iterable[float], percent: float) -> float:
    values = sorted(data)
    if not values:
        return 0.0
    k = (len(values) - 1) * (percent / 100.0)
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[int(k)]
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return d0 + d1


async def obtain_token(base_url: str, username: str, password: str) -> str:
    async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
        data = {"username": username, "password": password}
        resp = await client.post("/api/auth/login", data=data)
        resp.raise_for_status()
        return resp.json()["access_token"]


async def make_request(
    client: httpx.AsyncClient,
    endpoint: dict[str, Any],
    stats: TestStats,
) -> None:
    start = time.perf_counter()
    method = endpoint.get("method", "GET").upper()
    path = endpoint["path"]
    payload = endpoint.get("payload")
    try:
        resp = await client.request(method, path, json=payload)
        latency_ms = (time.perf_counter() - start) * 1000
        ok = resp.status_code < 500
        stats.results.append(
            RequestResult(
                latency_ms=latency_ms,
                ok=ok,
                status_code=resp.status_code,
                endpoint=path,
                error=None if ok else f"{resp.status_code}: {resp.text[:120]}",
            )
        )
    except Exception as exc:
        stats.results.append(
            RequestResult(
                latency_ms=None,
                ok=False,
                status_code=None,
                endpoint=path,
                error=str(exc),
            )
        )


async def run_load_test(
    base_url: str,
    token: str | None,
    concurrency: int,
    duration: int,
    endpoints: list[dict[str, Any]],
) -> TestStats:
    stats = TestStats(title="Load Test")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=20.0) as client:
        stop_at = time.monotonic() + duration
        async def worker() -> None:
            while time.monotonic() < stop_at:
                endpoint = random.choice(endpoints)
                await make_request(client, endpoint, stats)

        await asyncio.gather(*[worker() for _ in range(concurrency)])
    return stats


async def run_stress_test(
    base_url: str,
    token: str | None,
    start: int,
    maximum: int,
    step: int,
    endpoints: list[dict[str, Any]],
) -> list[TestStats]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    stats_collection: list[TestStats] = []
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=20.0) as client:
        current = start
        while current <= maximum:
            stats = TestStats(title=f"Stress Level {current}")
            tasks = [
                make_request(client, random.choice(endpoints), stats)
                for _ in range(current)
            ]
            await asyncio.gather(*tasks)
            stats_collection.append(stats)
            current += step
    return stats_collection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="اجرای تست کارایی")
    parser.add_argument("--base-url", default=os.getenv("PERF_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--username", default=os.getenv("PERF_USERNAME"))
    parser.add_argument("--password", default=os.getenv("PERF_PASSWORD"))
    parser.add_argument("--token", default=os.getenv("PERF_TOKEN"))
    parser.add_argument("--load-concurrency", type=int, default=10)
    parser.add_argument("--load-duration", type=int, default=60, help="مدت تست Load بر حسب ثانیه")
    parser.add_argument("--stress-start", type=int, default=5)
    parser.add_argument("--stress-max", type=int, default=50)
    parser.add_argument("--stress-step", type=int, default=5)
    parser.add_argument(
        "--endpoints",
        nargs="*",
        help="لیست endpoint ها به‌صورت method:path (مثلاً GET:/api/tickets)",
    )
    return parser


def parse_custom_endpoints(raw: list[str] | None) -> list[dict[str, Any]]:
    if not raw:
        return DEFAULT_ENDPOINTS
    parsed: list[dict[str, Any]] = []
    for item in raw:
        if ":" not in item:
            raise ValueError(f"فرمت endpoint نامعتبر است: {item}")
        method, path = item.split(":", 1)
        parsed.append({"method": method.strip().upper(), "path": path.strip()})
    return parsed


async def main_async() -> None:
    parser = build_parser()
    args = parser.parse_args()

    token = args.token
    if not token and args.username and args.password:
        token = await obtain_token(args.base_url, args.username, args.password)
    elif not token:
        print("⚠️  برای تست‌های محافظت‌شده باید token یا username/password ارائه شود.")

    endpoints = parse_custom_endpoints(args.endpoints)

    print("🚀 شروع Load Test ...")
    load_stats = await run_load_test(
        base_url=args.base_url,
        token=token,
        concurrency=args.load_concurrency,
        duration=args.load_duration,
        endpoints=endpoints,
    )
    print(load_stats.summary())

    print("⚡ شروع Stress Test ...")
    stress_stats = await run_stress_test(
        base_url=args.base_url,
        token=token,
        start=args.stress_start,
        maximum=args.stress_max,
        step=args.stress_step,
        endpoints=endpoints,
    )
    for stat in stress_stats:
        print(stat.summary())


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

