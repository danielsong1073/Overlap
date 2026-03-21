from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, auth
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not db_user or not auth.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = auth.create_access_token(data={"sub": db_user.username})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}