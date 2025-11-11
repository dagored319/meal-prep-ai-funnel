@echo off
REM Helper script to run the Organic Funnel Agent with virtual environment

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the main script with arguments
python main.py %*

REM Keep window open if there's an error
if errorlevel 1 pause
