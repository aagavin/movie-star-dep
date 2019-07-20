from starlette.routing import Mount
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import UJSONResponse
from src.api.search import SearchRouter
from src.api.account import AccountRouter
from src.api.media import MediaRouter
from . import config


DEBUG = config('DEBUG', cast=bool)
app: Starlette = Starlette(debug=DEBUG)


app.routes.extend(
    [
        Mount('/search', app=SearchRouter),
        Mount('/media', app=MediaRouter),
        Mount('/user', app=AccountRouter)
    ]
)


@app.route('/')
async def home(request: Request) -> UJSONResponse:
    return UJSONResponse({'success': True, 'query': dict(request.query_params)})
