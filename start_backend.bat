@echo off
echo 🚀 Starting FastAPI Backend Only
echo ================================================

cd chatbot
echo Starting FastAPI server on http://127.0.0.1:8000
echo FastAPI docs will be available at: http://127.0.0.1:8000/docs
echo.
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause

