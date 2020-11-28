from starlette.routing import Route, Router
from starlette.requests import Request
from starlette.responses import JSONResponse
from firebase_admin import auth, firestore


db = firestore.client()


async def create_account(request: Request) -> JSONResponse:
    body = await request.json()
    try:
        user = auth.create_user(
            email=body.get('email'),
            password=body.get('password'),
            phone_number=body.get('phone'),
            display_name=body.get('name'),
        )
    except ValueError as ve:
        return JSONResponse({'error': {'code': 400, 'message': ve.args[0]}}, 400)
    return JSONResponse({'name': user.uid})


AccountRouter = Router([
    Route('/create', endpoint=create_account, methods=['POST']),
    Route('/{user_id}', endpoint=lambda r: JSONResponse({}), methods=['GET']),
])
