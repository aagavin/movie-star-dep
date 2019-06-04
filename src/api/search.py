from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from starlette.datastructures import URL, Secret
from requests import Response
from .. import reqSession, config


API_KEY = config('API_KEY', cast=Secret)
BASE_URL = config('BASE_URL', cast=URL)


async def search_all(request: Request):
    endpoint = request.path_params.get('endpoint')
    if endpoint is None or endpoint not in ['movie', 'tv']:
        endpoint = 'multi'
    return await do_search(request, f'/search/{endpoint}')


async def do_search(request, url):
    query_params = {
        'api_key': API_KEY,
        'query': request.query_params.get('q')
    }
    result: Response = reqSession.get(f'{BASE_URL}{url}', params=query_params)
    return UJSONResponse(result.json()['results'])


SearchRouter = Router([
    Route('/', endpoint=search_all, methods=['GET']),
    Route('/{endpoint}', endpoint=search_all, methods=['GET'])
])
