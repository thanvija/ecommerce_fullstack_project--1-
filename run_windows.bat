@echo off
echo ============================================================================
echo Starting NovaCommerce Full-Stack Project (React + FastAPI + Django)
echo ============================================================================

echo [1/3] Starting FastAPI Business API Server on http://localhost:8000 ...
start "FastAPI Server (Port 8000)" cmd /k "cd /d %~dp0backend_fastapi && pip install fastapi uvicorn sqlalchemy pydantic[email] pyjwt bcrypt && uvicorn main:app --reload --port 8000"

echo [2/3] Starting Django Auth and Admin Server on http://localhost:8001 ...
start "Django Server (Port 8001)" cmd /k "cd /d %~dp0backend_django && pip install django djangorestframework djangorestframework-simplejwt django-cors-headers bcrypt pyjwt && python manage.py makemigrations core && python manage.py migrate && python manage.py runserver 8001"

echo [3/3] Starting React Frontend on http://localhost:3000 ...
start "React Frontend (Port 3000)" cmd /k "cd /d %~dp0frontend_react && npm install && npm run dev"

echo All services launched in separate Command Prompt windows!
pause
