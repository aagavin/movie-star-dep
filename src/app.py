from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import UJSONResponse
from src.routes import app
from src import redis_db
import base64
import ujson
import uvicorn


cached_paths = ['/search/', '/media/']


class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
        if any([request.url.path.startswith(path) for path in cached_paths]):
            cache = redis_db.get(encoded)
            if cache is not None:
                # print('using cache')
                return UJSONResponse(ujson.loads(cache))
        return await call_next(request)


app.add_middleware(CacheMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)


if __name__ == '__main__':
    uvicorn.run(app, port=3000)
