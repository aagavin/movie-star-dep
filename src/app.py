from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse
from src.routes import app
import base64
import json
import uvicorn


class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if "localhost" == request.base_url.hostname:
            response = await call_next(request)
            response.headers['X-FROM-CACHE'] = 'false'
            return response
        from src.db import RedisDatabase
        redis_async = RedisDatabase.redis_async
        encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
        if any(request.url.path.startswith(path) for path in ['/search/', '/media/']):
            cache = await redis_async.get(encoded, encoding='utf-8')
            if cache is not None:
                response: JSONResponse = JSONResponse(json.loads(cache))
                response.headers.append('X-FROM-CACHE', 'true')
                return response
        return await call_next(request)


app.add_middleware(CacheMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=['movie.aagavin.ca', 'localhost', 'watch-tv-list.herokuapp.com']
)
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

app.add_exception_handler(404, lambda r, e: JSONResponse(e))
app.add_exception_handler(500, lambda r, e: JSONResponse(e))


if __name__ == '__main__':
    uvicorn.run(app, port=3000)
