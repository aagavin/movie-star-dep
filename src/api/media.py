from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from json import dumps as json_dumps
from base64 import b64encode
from .. import imdb, ONE_WEEK_SECS


async def save_cache(url_path, query_params, data, status=200):
    from src.db import RedisDatabase
    redis_async = RedisDatabase.redis_async
    if status != 200:
        return
    encoded = b64encode(f'{url_path}-{query_params}'.encode('utf-8'))
    await redis_async.set(encoded, json_dumps(data), expire=ONE_WEEK_SECS)


async def get_media_by_id(request: Request) -> JSONResponse:
    media_id = request.path_params.get('media_id')
    response: dict = imdb.get_title_auxiliary(media_id)
    response['id'] = response['id'].split('/')[2]
    response.pop('nextEpisode', None)
    response.pop('soundtracks', None)
    response.pop('adWidgets', None)
    response.pop('productionStatus', None)
    response.pop('filmingLocations', None)
    response.pop('videos', None)
    response.pop('seasonsInfo', None)
    response.pop('numberOfVotes', None)
    response.pop('canRate', None)
    response.pop('topRank', None)
    response.pop('userRating', None)
    response.pop('alternateTitlesSample', None)
    task = BackgroundTask(save_cache, url_path=request.url.path, query_params=request.query_params, data=response)
    return JSONResponse(response, background=task)


async def get_media_episodes(request: Request) -> JSONResponse:
    media_id = request.path_params.get('media_id')
    response: dict = imdb.get_title_episodes(media_id)
    task = BackgroundTask(save_cache, url_path=request.url.path, query_params=request.query_params, data=response)
    return JSONResponse(response, background=task)


async def get_popular_media(request: Request) -> JSONResponse:
    media_type = request.path_params.get('media_type')
    if media_type == 'movies':
        popular_media = imdb.get_popular_movies()['ranks']
    else:
        popular_media = imdb.get_popular_shows()['ranks']
    popular_media = [{**media, 'id': media['id'].split('/')[2]} for media in popular_media]
    task = BackgroundTask(save_cache, url_path=request.url.path, query_params=request.query_params, data=popular_media)
    return JSONResponse(popular_media, background=task)


MediaRouter = Router([
    Route('/{media_type}/popular', endpoint=get_popular_media, methods=['GET']),
    Route('/{media_type}/{media_id}', endpoint=get_media_by_id, methods=['GET']),
    Route('/tv/{media_id}/episodes', endpoint=get_media_episodes, methods=['GET']),
])
