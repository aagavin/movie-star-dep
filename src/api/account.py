from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from firebase_admin.auth import AuthError
from firebase_admin import auth, firestore
from base64 import b64encode
from ujson import loads
from asyncio import gather
from .. import redis_db
from .media import get_media_by_id


db = firestore.client()


async def get_cached_result(media_id, media_type) -> dict or None:
    # /media/tv/76892-
    encoded = b64encode(f'/media/{media_type}/{media_id}-'.encode('utf-8'))
    cached_value = redis_db.get(encoded)
    if cached_value is None:
        return None
    return loads(cached_value)


async def create_account(request: Request) -> UJSONResponse:
    body = await request.json()
    try:
        user = auth.create_user(
            email=body.get('email'),
            email_verified=False,
            password=body.get('password'),
            phone_number=body.get('phone'),
            display_name=body.get('name'),
            disabled=False
        )
    except AuthError as ae:
        return UJSONResponse(ae.detail.response.json(), 400)
    except ValueError as ve:
        return UJSONResponse({'error': {'code': 400, 'message': ve.args[0]}}, 400)
    return UJSONResponse({'name': user.uid})


async def get_favourites(request: Request) -> UJSONResponse:
    # verify token
    try:
        token = request.headers.get('id_token')
        uid: dict = auth.verify_id_token(token)
    except ValueError as v:
        return UJSONResponse({'error': v.args}, 400)
    user_favs = db.collection('favs').document(uid.get('user_id')).get().to_dict()

    # get favouriest
    fav_results: list = []
    for fav in user_favs:
        cached_result = get_cached_result(fav, user_favs[fav]['catogery'])
        if cached_result is None:
            fav_results.append(get_media_by_id(request, True, fav, user_favs[fav]['catogery']))
        fav_results.append(cached_result)
    return UJSONResponse({'favs': await gather(*fav_results)})

AccountRouter = Router([
    Route('/create', endpoint=create_account, methods=['POST']),
    Route('/favourites', endpoint=get_favourites, methods=['GET']),
    Route('/{user_id}', endpoint=lambda r: UJSONResponse({}), methods=['GET']),
])
