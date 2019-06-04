from starlette.config import Config
from requests import Session
import requests


config = Config()
reqSession: Session = requests.session()
