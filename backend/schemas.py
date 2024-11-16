from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


# Models for Poem Type

class PoemTypeCreate(BaseModel):
    name: str = Field(..., max_length=50)
    description: str
    criteria: Dict[str, Any] 


class PoemTypeResponse(PoemTypeCreate):
    id: int

    class Config:
        from_attributes = True


# Models for PoemDetails

class PoemDetailsCreate(BaseModel):
    poem_id: int
    poet_id: int
    content: str = Field(..., min_length=1)
    publish: Optional[bool] = False


class PoemDetailsUpdate(BaseModel):
    id: Optional[int] = None
    content: Optional[str] = None


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


class PoemUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=250)
    poem_type_id: Optional[int]
    details: Optional[List[PoemDetailsUpdate]] = []


class PoemResponse(PoemCreate):
    id: int
    created_at: datetime
    details: Optional[List[PoemDetailsResponse]] = []
    is_published: Optional[bool] = False
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
