from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from requests import Response
from .. import reqSession, API_KEY, BASE_URL, redis_db, ONE_WEEK_SECS
from ujson import dumps as json_dumps
import base64


async def get_tv_by_id(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    movie_id = request.path_params.get('tv_id')
    result: Response = reqSession.get(f'{BASE_URL}/tv/{movie_id}', params={'api_key': API_KEY})
    redis_db.set(encoded, json_dumps(result.json()), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json())


async def get_popular_tv(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    result: Response = reqSession.get(f'{BASE_URL}/tv/popular', params={'api_key': API_KEY})
    redis_db.set(encoded, json_dumps(result.json()['results']), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json()['results'])


async def get_up_coming_tv(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    result: Response = reqSession.get(f'{BASE_URL}/tv/on_the_air', params={'api_key': API_KEY})
    redis_db.set(encoded, json_dumps(result.json()['results']), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json()['results'])


TvRouter = Router([
    Route('/popular', endpoint=get_popular_tv, methods=['GET']),
    Route('/upcoming', endpoint=get_up_coming_tv, methods=['GET']),
    Route('/{tv_id}', endpoint=get_tv_by_id, methods=['GET'])
])
