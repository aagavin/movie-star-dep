from aioredis import create_redis_pool
from starlette.config import Config


config = Config()
REDISCLOUD_URL = config('REDISCLOUD_URL')


class RedisDatabase:
    redis_async = None

    @staticmethod
    async def open_database_connection_pool():
        RedisDatabase.redis_async = await create_redis_pool(REDISCLOUD_URL)

    @staticmethod
    async def close_database_connection_pool():
        print('shutting down database')
        RedisDatabase.redis_async.close()
        await RedisDatabase.redis_async.wait_closed()
        print('closing database')
