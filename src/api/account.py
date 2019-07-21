from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from firebase_admin.auth import AuthError
from firebase_admin import auth, firestore

db = firestore.client()


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
    return UJSONResponse({'name': user.uid})


async def get_favourites(request: Request) -> UJSONResponse:
    token = request.headers.get('id_token')
    try:
        uid: dict = auth.verify_id_token(token)
    except ValueError as v:
        return UJSONResponse({'error': v.args}, 400)
    user_favs = db.collection('favs').document(uid.get('user_id')).get().to_dict()
    for fav in user_favs:
        if user_favs[fav]['catogery'] == 'movie':
            print('call move')
    return UJSONResponse({'favs': user_favs})

AccountRouter = Router([
    Route('/create', endpoint=create_account, methods=['POST']),
    Route('/favourites', endpoint=get_favourites, methods=['GET']),
    Route('/{user_id}', endpoint=lambda r: UJSONResponse({}), methods=['GET']),
])
