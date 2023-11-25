from jose import jwt
from fastapi import Depends
from datetime import timedelta, datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from starlette.authentication import AuthCredentials, UnauthenticatedUser


from src.settings import get_settings
from src.database import get_supabase_db, get_local_db
from models import ClientModel


settings = get_settings()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data,  expiry: timedelta):
    payload = data.copy()
    expire_in = datetime.utcnow() + expiry
    payload.update({"exp": expire_in})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def create_refresh_token(data):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def get_token_payload(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception as e:
        return None
    return payload

def get_current_client(token: str = Depends(oauth2_scheme), db = None, local = False):
    payload = get_token_payload(token)
    if not payload or type(payload) is not dict:
        return None

    client_id = payload.get('id', None)
    if not client_id:
        return None

    if not db:
        db = next(get_local_db()) if local else get_supabase_db()
    
    if local:
        client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    else:
        client = db.table('clients').select('*').eq('id', client_id).limit(1).execute().data[0]
    
    return client


class JWTAuthenticationBackend:
    async def authenticate(self, conn):
        guest = AuthCredentials(['unauthenticated']), UnauthenticatedUser()
        
        if 'authorization' not in conn.headers:
            return guest
        
        token = conn.headers.get('authorization').split(' ')[1]
        if not token:
            return guest
        
        user = get_current_client(token=token)
        
        if not user:
            return guest
        
        return AuthCredentials('authenticated'), user