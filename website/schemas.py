from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# This model will ensure that when a user submits data to create a new poet, 
# the input data is correctly formatted and valid before interacting with your database.
class PoetCreate(BaseModel):
    poet_name: str = Field(...,min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=7, max_length=20)


# This model is used to structure the data that gets sent back 
# when querying or returning a poet's information (e.g., in response to a request or query).
class PoetResponse(BaseModel):
    id: int
    poet_name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allows reading data from SQLAlchemy objects


class PoemCreate(BaseModel):
    title: str = Field(..., max_length=250)
    poem_type_id: int
    is_collaborative: Optional[bool] = False


# This model is used to return the poem's data after it is created or fetched from the database.
class PoemResponse(BaseModel):
    id: int
    title: str
    is_collaborative: bool
    created_at: datetime
    update_at: Optional[datetime]

    class Config:
        from_attributes = True


# Used to validate incoming data for creating new poem types.
class PoemTypeCreate(BaseModel):
    name: str = Field(..., max_length=50)
    description: str
    criteria: str


class PoemTypeResponse(BaseModel):
    id: int
    name: str
    description: str
    criteria: str

    class Config:
        from_attributes = True
