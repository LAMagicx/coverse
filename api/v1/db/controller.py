# db.py
import httpx
import json

from v1.common.settings import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NS, DB_DB

class DatabaseController:

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

    async def sql(self, query: str = "") -> dict:
        conn = await self.get_connection()
        res = await conn.post('/sql', data=query)
        res_json = json.loads(res.content)
        for response in res_json:
            if response['status'] == 'OK':
                yield response['result']
        else:
            yield []
