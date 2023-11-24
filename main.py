import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from src.routers import client_router, auth_router, user_router, ride_router
from src.services.security import JWTAuthenticationBackend

app = FastAPI()

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthenticationBackend())

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(client_router)
app.include_router(ride_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
