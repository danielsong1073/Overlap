import os
import uuid
import boto3
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from botocore.config import Config
from .. import models, schemas, auth
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", status_code=201, response_model=schemas.UserResponse)
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

    if not db_user:
        auth.verify_password(form_data.password, "dummy_hash")
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    if not auth.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: Annotated[str, Depends(get_current_user)]):
    return {"username": current_user}


@router.get("/{username}/shelf", response_model=list[schemas.EntryResponse])
def get_user_shelf(username: str, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.entries


@router.get("/suggested", response_model=list[schemas.SuggestedUserResponse])
def get_overlaps(current_user: Annotated[str, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    entries = user.entries
    overlaps = Counter()
    for entry in entries:
        overlap = db.query(models.Entry).filter(models.Entry.external_id == entry.external_id, models.Entry.external_id.isnot(None), models.Entry.user_id != user.id).all()
        for o in overlap:
            overlaps[o.owner.username] += 1

    return [schemas.SuggestedUserResponse(username=username, overlap_count=count) for username, count in overlaps.most_common()]


@router.get("/upload-url")
def get_upload_url(current_user: Annotated[str, Depends(get_current_user)]):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
        config=Config(signature_version="s3v4")
    )
    file_key = str(uuid.uuid4()) + ".jpg"
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": os.getenv("AWS_BUCKET_NAME"),
            "Key": file_key,
            "ContentType": "image/jpeg"
        },
        ExpiresIn=300
    )

    return {"upload_url": url, "file_key": file_key}


@router.put("/me/profile-picture", response_model=schemas.UserResponse)
def update_profile_picture(body: schemas.ProfilePictureUpdate,
                           current_user: Annotated[str, Depends(get_current_user)],
                           db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_picture = body.profile_picture_url
    
    db.commit()
    db.refresh(user)

    return user