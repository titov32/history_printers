from fastapi import Depends, APIRouter, Request

from .models import User
from .schemas import UserCreate, UserRead, UserUpdate
from .users import auth_backend, current_active_user, fastapi_users
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


templates = Jinja2Templates(directory="app/static/templates")
auth_router = APIRouter()

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@auth_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    print(f'user verified {user.is_verified}')
    print(f'user email {user.email}')
    return {"message": f"Hello {user.email}!"}


@auth_router.get("/login", response_class=HTMLResponse)
async def get_form_login(request: Request):

    context = {"request": request,
               }
    return templates.TemplateResponse("auth/login.html", context)