from aioredis import create_redis_pool, Redis
from starlette.config import Config


config = Config()
REDISCLOUD_URL = config('REDISCLOUD_URL')


redis_async = None


async def open_database_connection_pool():
    global redis_async
    redis_async = await create_redis_pool(REDISCLOUD_URL)


async def close_database_connection_pool():
    print('shutting down database')
    redis_async.close()
    await redis_async.wait_closed()
    print('\n..........\nclosing database')
