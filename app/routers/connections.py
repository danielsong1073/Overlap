from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .. import auth, models, schemas
from ..database import get_db


router = APIRouter(
    prefix="/connections",
    tags=["connections"]
)


@router.post("/{username}/send", response_model=schemas.ConnectionResponse, status_code=201)
def send_connection(current_user: Annotated[str, Depends(auth.get_current_user)], username: str, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    other_user = db.query(models.User).filter(models.User.username == username).first()
    if not other_user:
        raise HTTPException(status_code=400, detail="Cant' find user")
    if user == other_user:
        raise HTTPException(status_code=400, detail="Can't connect to yourself")
    existing = db.query(models.Connection).filter(
        or_(
            (models.Connection.requester_id == user.id) & (models.Connection.receiver_id == other_user.id),
            (models.Connection.requester_id == other_user.id) & (models.Connection.receiver_id == user.id)
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")

    new_connection = models.Connection(
        requester_id = user.id,
        receiver_id = other_user.id,
        status="pending"
    )

    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    return schemas.ConnectionResponse(
        requester_username=user.username,
        receiver_username=other_user.username,
        status=new_connection.status,
        created_at=new_connection.created_at
    )
    