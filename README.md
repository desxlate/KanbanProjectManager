# Kanban Project Manager
======================

Интерактивная канбан-доска с поддержкой проектов, задач, авторизации, drag-and-drop и красивым интерфейсом на Tailwind CSS.

## 🚀 Быстрый старт
----------------

### 🔧 1. Создай виртуальное окружение и активируй его:
--------------------

```
python -m venv .venv
.venv\Scripts\activate   # для Windows
source .venv/bin/activate  # для Linux/macOS
```

### 📦 2. Установи зависимости:
--------------------

```
pip install -r requirements.txt
```

### ▶️ 3. Запусти сервер:
--------------------

```
python -m uvicorn backend.main:app --reload
```

### 🌐 4. Открой в браузере:
--------------------

http://127.0.0.1:8000


### 📁 Структура проекта
--------------------

```
KanbanProjectManager/
├── backend/          # Сервер FastAPI + SQLAlchemy
├── frontend/         # HTML-фронтенд с Tailwind
├── requirements.txt  # Зависимости
├── .gitignore
└── README.md
```

### 🔐 Возможности
--------------

- Регистрация и вход по токену
- Создание/удаление проектов
- Создание задач с описанием, сроками, приоритетом и статусом
- Drag-and-drop задач между статусами
- Отображение прогресса проекта
- Поддержка нескольких пользователей

### 🛠️ Технологии
--------------

- Python + FastAPI
- SQLite + SQLAlchemy
- Tailwind CSS
- Vanilla JS (без фреймворков)
- JWT авторизация (`python-jose`, `passlib`)
