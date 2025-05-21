from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(UserCreate):
    hashed_password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    description: str
    priority: str
    assignee: str
    due_date: str
    status: str

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True