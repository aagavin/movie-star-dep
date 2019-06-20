from starlette.config import Config
from starlette.datastructures import Secret
from requests import Session
from firebase_admin import credentials
import firebase_admin
import requests


config = Config()

API_KEY = config('API_KEY', cast=Secret)
BASE_URL = config('BASE_URL')
project_id = config('project_id')
private_key_id = config('private_key_id')
private_key = config('private_key')
client_email = config('client_email')
client_id = config('client_id')
auth_uri = config('auth_uri')
token_uri = config('token_uri')
auth_provider_x509_cert_url = config('auth_provider_x509_cert_url')
client_x509_cert_url = config('client_x509_cert_url')
REDISCLOUD_URL = config('REDISCLOUD_URL')

reqSession: Session = requests.session()


cred = credentials.Certificate({
  "type": "service_account",
  "project_id": project_id,
  "private_key_id": private_key_id,
  "private_key": private_key.replace('\\\\n', '\n'),
  "client_email": client_email,
  "client_id": client_id,
  "auth_uri": auth_uri,
  "token_uri": token_uri,
  "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
  "client_x509_cert_url": client_x509_cert_url
})


firebase_app = firebase_admin.initialize_app(cred)
