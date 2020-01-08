from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from ujson import dumps as json_dumps
from base64 import b64encode
from .. import imdb, ONE_WEEK_SECS


async def save_cache(url_path, query_params, data, status=200):
    from src.db import RedisDatabase
    redis_async = RedisDatabase.redis_async
    if status != 200:
        return
    encoded = b64encode(f'{url_path}-{query_params}'.encode('utf-8'))
    await redis_async.set(encoded, json_dumps(data), expire=ONE_WEEK_SECS)


async def get_media_by_id(request: Request) -> UJSONResponse:
    media_id = request.path_params.get('media_id')
    response: dict = imdb.get_title_auxiliary(media_id)
    response['id'] = response['id'].split('/')[2]
    await save_cache(request.url.path, request.query_params, response, 200)
    return UJSONResponse(response)


async def get_popular_media(request: Request) -> UJSONResponse:
    media_type = request.path_params.get('media_type')
    if media_type == 'movies':
        popular_media = imdb.get_popular_movies()['ranks']
    else:
        popular_media = imdb.get_popular_shows()['ranks']
    popular_media = [{**media, 'id': media['id'].split('/')[2]} for media in popular_media]
    await save_cache(request.url.path, request.query_params, popular_media, 200)
    return UJSONResponse(popular_media)


MediaRouter = Router([
    Route('/{media_type}/popular', endpoint=get_popular_media, methods=['GET']),
    Route('/{media_type}/{media_id}', endpoint=get_media_by_id, methods=['GET']),
])
