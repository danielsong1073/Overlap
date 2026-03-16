from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db


router = APIRouter(
    prefix="/entries",
    tags=["entries"]
)


@router.post("/", response_model=schemas.EntryResponse)
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user).first()

    new_entry = models.Entry(
        media_type=entry.media_type,
        title=entry.title,
        status=entry.status,
        user_id=user.id
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.get("/me", response_model=list[schemas.EntryResponse])
def get_my_entires(db:Session = Depends(get_db), current_user: str = Depends(auth.get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    return user.entries


@router.put("/{entry_id}", response_model=schemas.EntryResponse)
def update_entry(entry_id: int, updated_entry: schemas.EntryCreate, db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id, models.Entry.user_id == user.id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry.media_type = updated_entry.media_type
    entry.title = updated_entry.title
    entry.status = updated_entry.status

    db.commit()
    db.refresh(entry)

    return entry