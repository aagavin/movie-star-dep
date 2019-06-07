from src.routes import app
from starlette.requests import Request
from starlette.responses import UJSONResponse
import uvicorn


@app.route('/')
async def home(request: Request) -> UJSONResponse:
    return UJSONResponse({'success': True, 'query': dict(request.query_params)})

if __name__ == '__main__':
    uvicorn.run(app, port=3000)
