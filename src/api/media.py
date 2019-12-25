from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from requests import Response
from time import sleep
from ujson import dumps as json_dumps
from base64 import b64encode
from .. import reqSession, imdb, API_KEY, BASE_URL, ONE_WEEK_SECS

user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'


async def save_cache(url_path, query_params, data, status):
    from src.db import RedisDatabase
    redis_async = RedisDatabase.redis_async
    if status != 200:
        return
    encoded = b64encode(f'{url_path}-{query_params}'.encode('utf-8'))
    await redis_async.set(encoded, json_dumps(data), expire=ONE_WEEK_SECS)


async def get_media_by_id(request: Request) -> UJSONResponse or dict:
    media_id = request.path_params.get('media_id')
    media_type = request.path_params['media_type']
    result: Response = reqSession.get(f'{BASE_URL}/{media_type}/{media_id}', params={'api_key': API_KEY})
    await save_cache(request.url.path, request.query_params, result.json(), result.status_code)
    return UJSONResponse(result.json())


async def get_media_by_id2(request: Request) -> UJSONResponse:
    media_id = request.path_params.get('media_id')
    return UJSONResponse(imdb.get_title_auxiliary(media_id))


async def get_popular_media(request: Request) -> UJSONResponse:
    result: Response = reqSession.get(
        f'{BASE_URL}/{request.path_params["media_type"]}/popular',
        params={'api_key': API_KEY}
    )
    await save_cache(request.url.path, request.query_params, result.json()['results'], result.status_code)
    return UJSONResponse(result.json()['results'])


async def get_popular_media2(request: Request) -> UJSONResponse:
    media_type = request.path_params.get('media_type')
    if media_type == 'movies':
        return UJSONResponse(imdb.get_popular_movies())
    return UJSONResponse(imdb.get_popular_shows())


async def get_up_coming(request: Request) -> UJSONResponse:
    media_type = request.path_params.get('media_type')
    media_path = 'on_the_air' if media_type == 'tv' else 'upcoming'
    result: Response = reqSession.get(
        f'{BASE_URL}/{media_type}/{media_path}',
        params={'api_key': API_KEY}
    )
    await save_cache(request.url.path, request.query_params, result.json()['results'], result.status_code)
    return UJSONResponse(result.json()['results'])


async def get_episodes_by_season(request: Request):
    tv_id = request.path_params.get('tv_id')
    season_number = request.path_params.get('season_number')
    episode_number = request.path_params.get('episode_number')
    sleep(.5)
    result: Response = reqSession.get(
        f'{BASE_URL}/tv/{tv_id}/season/{season_number}/episode/{episode_number}',
        params={'api_key': API_KEY}
    )
    await save_cache(request.url.path, request.query_params, result.json(), result.status_code)
    return UJSONResponse(result.json())

MediaRouter2 = Router([
    Route('/{media_type}/popular', endpoint=get_popular_media2, methods=['GET']),
    Route('/{media_type}/{media_id}', endpoint=get_media_by_id2, methods=['GET']),
])


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
