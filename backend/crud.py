from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from passlib.context import CryptContext
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, username: str) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    avatar_color = random_color()
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        avatar_color=avatar_color
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_task(db: Session, task: schemas.TaskCreate, user_id: int) -> models.Task:
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return (
        db.query(models.Task)
        .filter(models.Task.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_task(db: Session, task_id: int, updated_task: schemas.TaskBase, user_id: int) -> models.Task:
    db_task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == user_id)
        .first()
    )
    if not db_task:
        raise ValueError("Task not found")
    for key, value in updated_task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == user_id)
        .first()
    )
    if not db_task:
        raise ValueError("Task not found")
    db.delete(db_task)
    db.commit()

def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))