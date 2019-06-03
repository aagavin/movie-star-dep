from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.config import Config
from starlette.responses import UJSONResponse
from starlette.datastructures import URL, Secret
from requests import Response
import requests

config = Config()
API_KEY = config('API_KEY', cast=Secret)
BASE_URL = config('BASE_URL', cast=URL)


class Search(HTTPEndpoint):

    async def get(self, request: Request):
        query_params = {
            'api_key': API_KEY,
            'query': request.query_params.get('q')
        }
        result: Response = requests.get(f'{BASE_URL}/search/multi', params=query_params)
        return UJSONResponse(result.json()['results'])
