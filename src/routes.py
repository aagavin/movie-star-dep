from starlette.routing import Mount
from starlette.applications import Starlette
from src.api.search import SearchRouter


app: Starlette = Starlette(debug=True)


app.routes.append(Mount('/search', app=SearchRouter))
