from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from backend import crud, schemas, auth, database, models
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Настройка CORS
origins = [
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц при старте
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=database.engine)

# Регистрация пользователя
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# Авторизация (получение токена)
@app.post("/token")
def login_for_access_token(form_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Создание задачи
@app.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    current_user: schemas.UserResponse = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

# Получение задач
@app.get("/tasks/", response_model=list[schemas.TaskResponse])
def read_tasks(
    current_user: schemas.UserResponse = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
    skip: int = 0,
    limit: int = 100,
):
    return crud.get_tasks(db=db, user_id=current_user.id, skip=skip, limit=limit)

# Обновление задачи
@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    updated_task: schemas.TaskBase,
    current_user: schemas.UserResponse = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    try:
        return crud.update_task(db=db, task_id=task_id, updated_task=updated_task, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

# Удаление задачи
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: schemas.UserResponse = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    try:
        crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
        return {"detail": "Task deleted"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    
# Роут для главной страницы — отдаём index.html
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Автоматическое создание таблиц при старте
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=database.engine)