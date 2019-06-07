from starlette.routing import Mount
from starlette.applications import Starlette
from src.api.search import SearchRouter
from src.api.movie import MovieRouter
from src.api.tv import TvRouter
from . import config


DEBUG = config('DEBUG', cast=bool)
app: Starlette = Starlette(debug=DEBUG)


app.routes.extend(
    [
        Mount('/search', app=SearchRouter),
        Mount('/movie', app=MovieRouter),
        Mount('/tv', app=TvRouter),
    ]
)
