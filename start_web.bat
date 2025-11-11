@echo off
REM Start the chatbot web app

call venv\Scripts\activate.bat
echo.
echo ========================================
echo Starting Meal Prep Chatbot...
echo Open your browser to: http://localhost:8000
echo Press Ctrl+C to stop
echo ========================================
echo.
python main.py web
pause
