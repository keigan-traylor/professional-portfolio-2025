from contextlib import contextmanager
from functools import wraps
from typing import Callable, Dict
import asyncio, time

PLUGIN_REGISTRY: Dict[str, Callable] = {}

def register_plugin(name: str):
    def _decorator(fn: Callable):
        PLUGIN_REGISTRY[name] = fn
        return fn
    return _decorator

def timed(fn: Callable):
    if asyncio.iscoroutinefunction(fn):
        @wraps(fn)
        async def _async_wrapped(*args, **kwargs):
            t0 = time.perf_counter()
            result = await fn(*args, **kwargs)
            t1 = time.perf_counter()
            print(f"[timed] {fn.__name__} took {t1-t0:.4f}s")
            return result
        return _async_wrapped
    else:
        @wraps(fn)
        def _sync_wrapped(*args, **kwargs):
            t0 = time.perf_counter()
            result = fn(*args, **kwargs)
            t1 = time.perf_counter()
            print(f"[timed] {fn.__name__} took {t1-t0:.4f}s")
            return result
        return _sync_wrapped

@contextmanager
def managed_resource(name: str):
    print(f"[managed] acquiring {name}")
    try:
        yield {'name': name}
    finally:
        print(f"[managed] releasing {name}")
