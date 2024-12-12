from fastapi import Request, HTTPException
from .models import User


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    return User.get_or_none(User.id == user_id)