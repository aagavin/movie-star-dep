from starlette.routing import Mount
from starlette.applications import Starlette
from src.api.search import SearchRouter
from . import config


DEBUG = config('DEBUG', cast=bool)
app: Starlette = Starlette(debug=DEBUG)


app.routes.append(Mount('/search', app=SearchRouter))
