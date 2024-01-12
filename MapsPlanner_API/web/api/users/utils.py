from fastapi import HTTPException
from starlette import status


def validate_request(current_user, requested_user_id):
    if not (requested_user_id == current_user.id or current_user.is_administrator):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Such user."
        )
