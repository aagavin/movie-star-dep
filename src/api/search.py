from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from .. import reqSession, API_KEY, BASE_URL
from requests import Response


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
    response = [x for x in result.json()['results'] if x['media_type'] in ['movie', 'tv']]
    return UJSONResponse(response)


SearchRouter = Router([
    Route('/', endpoint=search_all, methods=['GET']),
    Route('/{endpoint}', endpoint=search_all, methods=['GET'])
])
