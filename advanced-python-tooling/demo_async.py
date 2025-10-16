import asyncio, random
from tools import PLUGIN_REGISTRY, register_plugin, timed, managed_resource

@register_plugin('task_alpha')
@timed
async def alpha(x):
    await asyncio.sleep(random.random()*0.2)
    return x*2

@register_plugin('task_beta')
@timed
async def beta(x):
    await asyncio.sleep(random.random()*0.3)
    return x+3

from contextlib import asynccontextmanager
@asynccontextmanager
async def managed_ctx(name):
    with managed_resource(name) as res:
        yield res

async def worker(name, queue):
    while not queue.empty():
        item = await queue.get()
        plugin = PLUGIN_REGISTRY.get(item['task'])
        if plugin:
            async with managed_ctx(item['task']):
                res = await plugin(item['value'])
                print(f"Worker {name} processed {item} -> {res}")
        queue.task_done()

async def main():
    q = asyncio.Queue()
    for i in range(10):
        q.put_nowait({'task': 'task_alpha' if i%2==0 else 'task_beta', 'value': i})
    workers = [asyncio.create_task(worker(f'w{i}', q)) for i in range(3)]
    await q.join()
    for w in workers:
        w.cancel()

if __name__ == '__main__':
    asyncio.run(main())
