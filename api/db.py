# db.py
import httpx
from contextlib import asynccontextmanager

from settings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NS, DB_DB

class Database:

    def __init__(self):
        self.host = DB_HOST
        self.port = DB_PORT
        self.username = DB_USER
        self.password = DB_PASS
        self.ns = DB_NS
        self.db = DB_DB
        self.max_pool_size = 5
        self.auth = httpx.BasicAuth(username=self.username, password=self.password)

        self._connection_pool = {}
        self.conn = None

    async def get_connection(self) -> httpx.AsyncClient:
        if len(self._connection_pool) < self.max_pool_size:
            print(f"Created new client: http://{self.host}:{self.port}")
            client = httpx.AsyncClient(base_url=f"http://{self.host}:{self.port}", headers={"Accept": "application/json", "Content-Type":"text/plain", "NS":self.ns, "DB":self.db}, auth=self.auth)
            self._connection_pool[id(client)] = client
        else:
            client = next(iter(self._connection_pool.values()))
        return client

    async def close(self):
        for client_id in list(self._connection_pool.keys()):
            await self._connection_pool[client_id].aclose()
            del self._connection_pool[client_id]


