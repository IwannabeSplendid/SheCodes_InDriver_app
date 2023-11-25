from fastapi import APIRouter, status, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from src.database import get_supabase_db
from src.services import get_token, get_refresh_token

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

@auth_router.post("/token", status_code=status.HTTP_200_OK)
async def authenticate_user(data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_supabase_db)):
    return await get_token(data=data, db=db)

@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(refresh_token: str = Header(), db = Depends(get_supabase_db)):
    return await get_refresh_token(token=refresh_token, db=db)