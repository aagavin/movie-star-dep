from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from .. import reqXSession
from httpx import Response


async def search_all(request: Request):
    query: str = request.query_params.get('q')
    results: Response = await reqXSession.get(f'https://v2.sg.media-imdb.com/suggestion/{query[:1]}/{query.replace(" ", "_")}.json')
    response = []
    for result in results.json()['d']:
        if result.get('q') in ['TV series', 'TV mini-series', 'feature']:
            response.append({
                **result,
                'image': {
                    'url': result['i']['imageUrl']
                },
                'title': result['l']
            })

    return UJSONResponse(response)


SearchRouter = Router([
    Route('/', endpoint=search_all, methods=['GET']),
    Route('/{endpoint}', endpoint=search_all, methods=['GET'])
])
