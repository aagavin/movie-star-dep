from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import UJSONResponse
import uvicorn


app = Starlette(debug=True)


@app.route('/')
async def home(request: Request) -> UJSONResponse:
    return UJSONResponse({'success': True, 'query': dict(request.query_params)})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3000)
