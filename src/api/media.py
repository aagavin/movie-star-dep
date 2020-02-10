from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.background import BackgroundTask
from starlette.responses import UJSONResponse
from ujson import dumps as json_dumps
from lxml import html
from lxml.html import HtmlElement
from base64 import b64encode
from httpx import Response
from .. import imdb, ONE_WEEK_SECS, reqXSession


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
    task = BackgroundTask(save_cache, url_path=request.url.path, query_params=request.query_params, data=response)
    return UJSONResponse(response, background=task)


async def get_media_episodes(request: Request) -> UJSONResponse:
    media_id = request.path_params.get('media_id')
    response: dict = imdb.get_title_episodes(media_id)
    task = BackgroundTask(save_cache, url_path=request.url.path, query_params=request.query_params, data=response)
    return UJSONResponse(response, background=task)


async def get_tv_next_episode(request: Request) -> UJSONResponse:
    media_id = request.path_params.get('media_id')
    page: Response = await reqXSession.get(f'https://www.imdb.com/title/{media_id}/episodes')
    document = html.document_fromstring(page.text)
    try:
        element: HtmlElement = document.get_element_by_id('nextEpisode')
    except KeyError:
        return UJSONResponse({}, status_code=404)
    air_text: str = element.getchildren()[0].text.split('airs')[1][:-1]
    return UJSONResponse({'next_episode': air_text})


async def get_popular_media(request: Request) -> UJSONResponse:
    media_type = request.path_params.get('media_type')
    if media_type == 'movies':
        popular_media = imdb.get_popular_movies()['ranks']
    else:
        popular_media = imdb.get_popular_shows()['ranks']
    popular_media = [{**media, 'id': media['id'].split('/')[2]} for media in popular_media]
    task = BackgroundTask(save_cache, url_path=request.url.path, query_params=request.query_params, data=popular_media)
    return UJSONResponse(popular_media, background=task)


MediaRouter = Router([
    Route('/{media_type}/popular', endpoint=get_popular_media, methods=['GET']),
    Route('/{media_type}/{media_id}', endpoint=get_media_by_id, methods=['GET']),
    Route('/tv/{media_id}/episodes', endpoint=get_media_episodes, methods=['GET']),
    Route('/tv/{media_id}/next_episode', endpoint=get_tv_next_episode, methods=['GET'])
])
