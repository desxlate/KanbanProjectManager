from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from backend import crud, schemas, auth, database, models
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Project
from backend.schemas import ProjectCreate, ProjectOut

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц при старте
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=database.engine)

# ====== Аутентификация и регистрация ======

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

# ====== Проекты ======

@app.post("/projects/", response_model=ProjectOut)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Project).filter(Project.owner_id == current_user.id).all()

@app.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}

# ====== Задачи ======

@app.post("/tasks/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, current_user: schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks/", response_model=List[schemas.TaskResponse])
def read_tasks(current_user: schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_tasks(db=db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/projects/{project_id}/tasks", response_model=List[schemas.TaskResponse])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(models.Task).filter(
        models.Task.project_id == project_id,
        models.Task.owner_id == current_user.id
    ).all()

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, updated_task: schemas.TaskBase, current_user: schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return crud.update_task(db=db, task_id=task_id, updated_task=updated_task, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

@app.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def patch_task_status(task_id: int, updated_fields: dict, current_user: schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in updated_fields.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: schemas.UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
        return {"detail": "Task deleted"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

# ====== Главная страница ======

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())