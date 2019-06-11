from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from requests import Response
from .. import reqSession, API_KEY, BASE_URL


async def get_tv_by_id(request: Request) -> UJSONResponse:
    movie_id = request.path_params.get('movie_id')
    result: Response = reqSession.get(f'{BASE_URL}/tv/{movie_id}', params={'api_key': API_KEY})
    return UJSONResponse(result.json())


async def get_popular_tv(request: Request) -> UJSONResponse:
    result: Response = reqSession.get(f'{BASE_URL}/tv/popular', params={'api_key': API_KEY})
    return UJSONResponse(result.json()['results'])


async def get_up_coming_tv(request: Request) -> UJSONResponse:
    result: Response = reqSession.get(f'{BASE_URL}/tv/latest', params={'api_key': API_KEY})
    return UJSONResponse(result.json()['results'])


TvRouter = Router([
    Route('/popular', endpoint=get_popular_tv, methods=['GET']),
    Route('/upcoming', endpoint=get_up_coming_tv, methods=['GET']),
    Route('/{movie_id}', endpoint=get_tv_by_id, methods=['GET'])
])
