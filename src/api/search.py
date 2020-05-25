from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from .. import reqXSession
from httpx import Response


async def search_all(request: Request):
    query: str = request.query_params.get('q')
    results: Response = await reqXSession.get(f'https://v2.sg.media-imdb.com/suggestion/{query[:1].lower()}/{query.replace(" ", "_")}.json')
    response = []
    json_results = results.json().get('d')
    if json_results is None:
        return UJSONResponse([])
    for result in json_results:
        if result.get('q') in ['TV series', 'TV mini-series', 'feature']:
            response.append({
                **result,
                'image': {
                    'url': result['i']['imageUrl'] if result.get('i') is not None else ''
                },
                'title': result['l']
            })

    return UJSONResponse(response)


SearchRouter = Router([
    Route('/', endpoint=search_all, methods=['GET']),
    Route('/{endpoint}', endpoint=search_all, methods=['GET'])
])
