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


AccountRouter = Router([
    Route('/create', endpoint=create_account, methods=['POST']),
    Route('/{user_id}', endpoint=lambda r: UJSONResponse({}), methods=['GET'])
])
