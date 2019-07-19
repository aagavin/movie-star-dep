from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import UJSONResponse
from firebase_admin import auth


async def create_account(request: Request) -> UJSONResponse:
    body = await request.json()
    user = auth.create_user(
        email=body['email'],
        email_verified=False,
        password=body['password'],
        phone_number=body['phone'],
        display_name=body['name'],
        disabled=False)
    return UJSONResponse({'name': user.uid})


async def get_favourites(request: Request) -> UJSONResponse:
    token = request.headers.get('id_token')
    uid: dict = auth.verify_id_token(token)
    if uid.get('user_id') is None:
        return UJSONResponse({'err': 'sdfsdfsf'})

    return UJSONResponse({id: uid})

AccountRouter = Router([
    Route('/create', endpoint=create_account, methods=['POST']),
    Route('/favourites', endpoint=get_favourites, methods=['GET']),
    Route('/{user_id}', endpoint=lambda r: UJSONResponse({}), methods=['GET']),
])
