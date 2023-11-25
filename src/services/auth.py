from models import ClientModel, TokenResponse
from fastapi.exceptions import HTTPException
from .security import verify_password, create_access_token, create_refresh_token, get_token_payload
from src.settings import get_settings
from datetime import timedelta


settings = get_settings()


async def get_token(data, db, local = False):
    if local:
        client = db.query(ClientModel).filter(ClientModel.email == data.username).first()
    else:
        client= db.table('clients').select('*').eq('email', data.username).limit(1).execute().data

    if len(client) == 0:
        raise HTTPException(
            status_code=400,
            detail="Email is not registered with us.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(data.password, client[0]["password"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid Login Credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await _get_user_token(client=client[0])


async def get_refresh_token(token, db, local = False):   
    payload =  get_token_payload(token=token)
    user_id = payload.get('id', None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if local:
        user = db.query(ClientModel).filter(ClientModel.id == user_id).first()
    else:
        user = db.table('clients').select('*').eq('id', user_id).limit(1).execute().data

    if len(user) == 0:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _get_user_token(user=user[0], refresh_token=token)


async def _get_user_token(client, refresh_token = None):
    payload = {"id": client['id']}
    
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(payload, access_token_expiry)

    if not refresh_token:
        refresh_token = await create_refresh_token(payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expiry.seconds
    )
