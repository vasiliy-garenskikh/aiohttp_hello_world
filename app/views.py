from http import HTTPStatus
from json import JSONDecodeError
from aiohttp import web

from authorization.decorators import jwt_required
from models import User
from schema import UserSchema, UserParams


@jwt_required
async def get_users(request):
    user = await User.query.gino.all()
    user_schema = UserSchema(many=True)

    resp = {
        'items': user_schema.dump(user).data,
        'total': len(user),
    }
    return web.json_response(resp)


@jwt_required
async def get_user(request):
    user_schema = UserSchema()
    id_ = int(request.match_info.get('user_id'))
    user = await User.query.where(User.id == id_).gino.first()
    resp = {
        'user': user_schema.dump(user).data,
    }
    return web.json_response(resp)


@jwt_required
async def post_user(request):
    params = UserParams()
    try:
        data = await request.json()
    except JSONDecodeError:
        resp = {
            'data': {
                'message': 'No json in request body',
            },
            'status': HTTPStatus.UNPROCESSABLE_ENTITY,
        }
        return web.json_response(**resp)

    query = params.load(data)
    if query.errors:
        resp = {
            'data': {
                'message': 'No nickname provided',
            },
            'status': HTTPStatus.UNPROCESSABLE_ENTITY,
        }
        return web.json_response(**resp)

    nickname = data['nickname']

    user = await User.query.where(User.nickname == nickname).gino.first()
    if user:
        resp = {
            'data': {
                'message': 'Nickname is already taken',
            },
            'status': HTTPStatus.UNPROCESSABLE_ENTITY,
        }
        return web.json_response(**resp)

    await User.create(nickname=nickname)

    return web.HTTPCreated()
