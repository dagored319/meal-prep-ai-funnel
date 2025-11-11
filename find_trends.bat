@echo off
REM Find trending topics

call venv\Scripts\activate.bat
echo.
echo ========================================
echo Finding Trending Topics...
echo ========================================
echo.
python main.py trend
pause
