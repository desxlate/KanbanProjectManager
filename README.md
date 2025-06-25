виртуальное окружение:

# bash
python -m venv .venv
.venv\Scripts\activate

установи зависимости:

# bash
pip install -r requirements.txt

запусти сервер:

# bash
python -m uvicorn backend.main:app

открой в браузере:

http://127.0.0.1:8000