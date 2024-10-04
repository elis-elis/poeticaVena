from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# This model will ensure that when a user submits data to create a new poet, 
# the input data is correctly formatted and valid before interacting with your database.
class PoetCreate(BaseModel):
    poet_name: str = Field(..., max_length=50)
    email = EmailStr
    password = str(..., max_length=20)


# This model is used to structure the data that gets sent back 
# when querying or returning a poet's information (e.g., in response to a request or query).
class PoetResponse(BaseModel):
    id: int
    poet_name: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True  # Allows reading data from SQLAlchemy objects



