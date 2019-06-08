from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from functools import lru_cache
from requests import Response
from .. import reqSession, API_KEY, BASE_URL


@lru_cache(maxsize=64)
async def get_movie_by_id(request: Request) -> UJSONResponse:
    movie_id = request.path_params.get('movie_id')
    result: Response = reqSession.get(f'{BASE_URL}/movie/{movie_id}', params={'api_key': API_KEY})
    return UJSONResponse(result.json())


@lru_cache(maxsize=64)
async def get_popular_movie(request: Request) -> UJSONResponse:
    result: Response = reqSession.get(f'{BASE_URL}/movie/popular', params={'api_key': API_KEY})
    return UJSONResponse(result.json()['results'])


@lru_cache(maxsize=64)
async def get_up_coming(request: Request) -> UJSONResponse:
    result: Response = reqSession.get(f'{BASE_URL}/movie/upcoming', params={'api_key': API_KEY})
    return UJSONResponse(result.json()['results'])


MovieRouter = Router([
    Route('/popular', endpoint=get_popular_movie, methods=['GET']),
    Route('/upcoming', endpoint=get_popular_movie, methods=['GET']),
    Route('/{movie_id}', endpoint=get_movie_by_id, methods=['GET'])
])
