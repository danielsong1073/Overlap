from pydantic import BaseModel
from enum import Enum

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class SuggestedUserResponse(BaseModel):
    username: str
    overlap_count: int


class MediaType(str, Enum):
    book = "book"
    movie = "movie"
    tv = "tv"
    game = "game"


class Status(str, Enum):
    reading = "reading"
    watching = "watching"
    finished = "finished"
    dropped = "dropped"
    playing = "playing"


class EntryCreate(BaseModel):
    media_type: MediaType
    title: str
    status: Status


class EntryResponse(BaseModel):
    id: int
    media_type: str
    title: str
    status: str
    user_id: int
    external_id: str | None
    cover_image: str | None
    release_year: int | None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str