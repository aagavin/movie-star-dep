from src.routes import app
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse
from src import REDISCLOUD_URL
import ujson
import uvicorn
import base64
import redis


cached_paths = ['/search/', '/tv/', '/movie/']
redis_db = redis.from_url(REDISCLOUD_URL)
ONE_WEEK_SECS = 604800
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)


@app.middleware("http")
async def dispatch(request, call_next) -> Response:
    encoded = base64.b64encode(f'{request.url.path}-{request.path_params}-{request.query_params}'.encode('utf-8'))
    if any([request.url.path.startswith(path) for path in cached_paths]):
        cache = redis_db.get(encoded)
        if cache is not None:
            return UJSONResponse(ujson.loads(cache))
        response = await call_next(request)
        return_body = b''
        async for body in response.body_iterator:
            return_body += body
        redis_db.set(encoded, return_body, ex=ONE_WEEK_SECS)
    return await call_next(request)


@app.route('/')
async def home(request: Request) -> UJSONResponse:
    return UJSONResponse({'success': True, 'query': dict(request.query_params)})

if __name__ == '__main__':
    uvicorn.run(app, port=3000)
