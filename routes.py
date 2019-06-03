from starlette.routing import Route, Router
from api.search import Search


app = Router([
    Route('/search', endpoint=Search),
])
