from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from requests import Response
from .. import reqSession, API_KEY, BASE_URL, redis_db, ONE_WEEK_SECS
from ujson import dumps as json_dumps
import base64


async def request_by_id(media_type, id) -> Response:
    return reqSession.get(
        f'{BASE_URL}/{media_type}/{id}',
        params={'api_key': API_KEY}
    )


async def get_media_by_id(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    media_id = request.path_params.get('media_id')
    result = await request_by_id(request.path_params["media_type"], media_id)
    redis_db.set(encoded, json_dumps(result.json()), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json())


async def get_popular_media(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    result: Response = reqSession.get(
        f'{BASE_URL}/{request.path_params["media_type"]}/popular',
        params={'api_key': API_KEY}
    )
    redis_db.set(encoded, json_dumps(result.json()['results']), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json()['results'])


async def get_up_coming(request: Request) -> UJSONResponse:
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    media_type = request.path_params.get('media_type')
    media_path = 'on_the_air' if media_type == 'tv' else 'upcoming'
    result: Response = reqSession.get(
        f'{BASE_URL}/{media_type}/{media_path}',
        params={'api_key': API_KEY}
    )
    redis_db.set(encoded, json_dumps(result.json()['results']), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json()['results'])


async def get_episodes_by_season(request: Request):
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    tv_id = request.path_params.get('tv_id')
    season_number = request.path_params.get('season_number')
    episode_number = request.path_params.get('episode_number')
    result: Response = reqSession.get(
        f'{BASE_URL}/tv/{tv_id}/season/{season_number}/episode/{episode_number}',
        params={'api_key': API_KEY}
    )
    redis_db.set(encoded, json_dumps(result.json()), ex=ONE_WEEK_SECS)
    return UJSONResponse(result.json())


MediaRouter = Router([
    Route('/{media_type}/popular', endpoint=get_popular_media, methods=['GET']),
    Route('/{media_type}/upcoming', endpoint=get_up_coming, methods=['GET']),
    Route('/{media_type}/{media_id}', endpoint=get_media_by_id, methods=['GET']),
    Route(
        '/tv/{tv_id}/season/{season_number}/episode/{episode_number}',
        endpoint=get_episodes_by_season,
        methods=['GET']
    )
])
