from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from .. import reqSession, API_KEY, BASE_URL, redis_db, ONE_WEEK_SECS
from requests import Response
from ujson import dumps as json_dumps
import base64


async def search_all(request: Request):
    encoded = base64.b64encode(f'{request.url.path}-{request.query_params}'.encode('utf-8'))
    endpoint = request.path_params.get('endpoint')
    if endpoint is None or endpoint not in ['movie', 'tv']:
        endpoint = 'multi'
    response = await do_search(request.query_params.get('q'), f'/search/{endpoint}')
    redis_db.set(encoded, json_dumps(response), ex=ONE_WEEK_SECS)
    return UJSONResponse(response)


async def do_search(search_query, url):
    query_params = {
        'api_key': API_KEY,
        'query': search_query
    }
    result: Response = reqSession.get(f'{BASE_URL}{url}', params=query_params)
    response = [x for x in result.json()['results'] if x['media_type'] in ['movie', 'tv']]
    return response


SearchRouter = Router([
    Route('/', endpoint=search_all, methods=['GET']),
    Route('/{endpoint}', endpoint=search_all, methods=['GET'])
])
