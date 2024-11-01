from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# Models for Poem Type

class PoemTypeCreate(BaseModel):
    name: str = Field(..., max_length=50)
    description: str
    criteria: str


class PoemTypeResponse(PoemTypeCreate):
    id: int

    class Config:
        from_attributes = True


# Models for PoemDetails

class PoemDetailsCreate(BaseModel):
    poem_id: int
    poet_id: int
    content: str = Field(..., min_length=5)


class PoemDetailsResponse(PoemDetailsCreate):
    id: int
    submitted_at: datetime

    class Config:
        from_attributes = True


# Models for Poet

class PoetCreate(BaseModel):
    poet_name: str = Field(..., min_length=3)
    email: EmailStr
    password_hash: str = Field(..., min_length=7)


class PoetResponse(PoetCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Allows reading data from SQLAlchemy objects


# Models for Poem

class PoemCreate(BaseModel):
    title: str = Field(..., max_length=250)
    poem_type_id: int
    poet_id: int
    is_collaborative: Optional[bool] = False


class PoemResponse(PoemCreate):
    id: int
    is_published: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    details: Optional[PoemDetailsCreate] = []

    class Config:
        from_attributes = True
