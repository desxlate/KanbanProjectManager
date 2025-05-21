# Kanban Project Manager

Это веб-приложение для управления задачами по методологии Kanban.

## 💡 Возможности
- Регистрация и авторизация через JWT
- CRUD операции с задачами
- Drag-and-drop между колонками
- Минимальный дизайн через TailwindCSS
- Хранение данных в SQLite

## 🛠️ Технологии
- FastAPI
- SQLAlchemy
- JWT
- HTML/CSS/JS (все в одном файле)

## 📦 Установка
```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
