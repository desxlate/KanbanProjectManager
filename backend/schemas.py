from pydantic import BaseModel
from datetime import date
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    avatar_color: str

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: str
    priority: str
    assignee: Optional[str] = None
    due_date: date
    status: str
    project_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int

    class Config:
        from_attributes = True