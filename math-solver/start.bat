@echo off
echo Starting Math Problem Solver...

echo Starting Backend...
cd backend
start "Backend" python main.py
cd ..

echo Waiting for backend to start...
timeout /t 5 /nobreak

echo Starting Frontend...
cd frontend
start "Frontend" npm run dev
cd ..

echo Application started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs

pause