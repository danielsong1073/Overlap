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
        status=schemas.ConnectionStatus.pending
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
    

@router.put("/{username}/accept", response_model=schemas.ConnectionResponse)
def accept_connection(current_user: Annotated[str, Depends(auth.get_current_user)], username: str, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    other_user = db.query(models.User).filter(models.User.username == username).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    connection = db.query(models.Connection).filter(models.Connection.requester_id == other_user.id, models.Connection.receiver_id == user.id).first()
    if not connection:
        raise HTTPException(status_code=400, detail="Connection doesn't exist")
    connection.status="accepted"
    db.commit()
    db.refresh(connection)

    return schemas.ConnectionResponse(
        requester_username=user.username,
        receiver_username=other_user.username,
        status=connection.status,
        created_at=connection.created_at
    )


@router.put("/{username}/decline", response_model=schemas.ConnectionResponse)
def decline_connection(current_user: Annotated[str, Depends(auth.get_current_user)], username: str, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    other_user = db.query(models.User).filter(models.User.username == username).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    connection = db.query(models.Connection).filter(models.Connection.requester_id == other_user.id, models.Connection.receiver_id == user.id).first()
    if not connection:
        raise HTTPException(status_code=400, detail="Connection doesn't exist")
    connection.status="declined"
    db.commit()
    db.refresh(connection)

    return schemas.ConnectionResponse(
        requester_username=user.username,
        receiver_username=other_user.username,
        status=connection.status,
        created_at=connection.created_at
    )


@router.get("/", response_model=list[schemas.ConnectionResponse])
def get_connections(current_user: Annotated[str, Depends(auth.get_current_user)], db: Annotated[Session, Depends(get_db)], status: schemas.ConnectionStatus):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    connections = db.query(models.Connection).filter(
        models.Connection.status == status,
        or_(
            models.Connection.requester_id == user.id,
            models.Connection.receiver_id == user.id
        )
    ).all()
    my_connections = []
    for connection in connections:
        requester = db.query(models.User).filter(models.User.id == connection.requester_id).first()
        receiver = db.query(models.User).filter(models.User.id == connection.receiver_id).first()
        my_connections.append(schemas.ConnectionResponse(
            requester_username=requester.username,
            receiver_username=receiver.username,
            status=connection.status,
            created_at=connection.created_at
        ))
    return my_connections


@router.delete("/{username}", status_code=204)
def delete_connections(current_user: Annotated[str, Depends(auth.get_current_user)], db: Annotated[Session, Depends(get_db)], username: str):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    other_user = db.query(models.User).filter(models.User.username == username).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    connection = db.query(models.Connection).filter(
        or_((models.Connection.requester_id == user.id) & (models.Connection.receiver_id == other_user.id),
            (models.Connection.requester_id == other_user.id) & (models.Connection.receiver_id == user.id))
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(connection)
    db.commit()
