import requests
import time
import asyncio
import httpx


URL = "https://api-adresse.data.gouv.fr/search/"
PARAMS = {
    "q": "8 bd du port",
    "limit": 1
}
N = 100

def test_requests():
    start = time.perf_counter()
    for _ in range(N):
        r = requests.get(URL, params=PARAMS)
        r.raise_for_status()
    return time.perf_counter() - start

def test_httpx_sync():
    start = time.perf_counter()
    with httpx.Client() as client:
        for _ in range(N):
            r = client.get(URL, params=PARAMS)
            r.raise_for_status()
    return time.perf_counter() - start

async def fetch(client):
    r = await client.get(URL, params=PARAMS)
    r.raise_for_status()

async def test_httpx_async():
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client) for _ in range(N)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    duration = test_requests()
    print(f"requests: {duration:.3f}s ({N/duration:.2f} req/s)")
    time.sleep(1)
    duration = test_httpx_sync()
    print(f"httpx sync: {duration:.3f}s ({N/duration:.2f} req/s)")
    time.sleep(1)
    start = time.perf_counter()
    asyncio.run(test_httpx_async())
    duration = time.perf_counter() - start
    print(f"httpx async: {duration:.3f}s ({N/duration:.2f} req/s)")
