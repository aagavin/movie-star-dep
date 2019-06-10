from src.routes import app
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import UJSONResponse
import uvicorn


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)
# app.add_middleware(CustomHeaderMiddleware)


@app.route('/')
async def home(request: Request) -> UJSONResponse:
    return UJSONResponse({'success': True, 'query': dict(request.query_params)})

if __name__ == '__main__':
    uvicorn.run(app, port=3000)
