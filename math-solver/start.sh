#!/bin/bash

echo "Starting Math Problem Solver..."

echo "Starting Backend..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to start..."
sleep 5

echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Application started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"

# Wait for user to stop
echo "Press Ctrl+C to stop..."
wait