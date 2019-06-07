from starlette.config import Config
from starlette.datastructures import URL, Secret
from requests import Session
import requests


config = Config()

API_KEY = config('API_KEY', cast=Secret)
BASE_URL = config('BASE_URL', cast=URL)


reqSession: Session = requests.session()
