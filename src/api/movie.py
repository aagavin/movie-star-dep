from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from requests import Response
from .. import reqSession, API_KEY, BASE_URL, redis_db, ONE_WEEK_SECS
from ujson import dumps as json_dumps
import base64


async def get_movie_by_id(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    movie_id = request.path_params.get('movie_id')
    result: Response = reqSession.get(f'{BASE_URL}/movie/{movie_id}', params={'api_key': API_KEY})
    redis_db.set(encoded, json_dumps(result.json()), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json())


async def get_popular_movie(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    result: Response = reqSession.get(f'{BASE_URL}/movie/popular', params={'api_key': API_KEY})
    redis_db.set(encoded, json_dumps(result.json()['results']), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json()['results'])


async def get_up_coming(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    result: Response = reqSession.get(f'{BASE_URL}/movie/upcoming', params={'api_key': API_KEY})
    redis_db.set(encoded, json_dumps(result.json()['results']), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json()['results'])


MovieRouter = Router([
    Route('/popular', endpoint=get_popular_movie, methods=['GET']),
    Route('/upcoming', endpoint=get_up_coming, methods=['GET']),
    Route('/{movie_id}', endpoint=get_movie_by_id, methods=['GET'])
])
