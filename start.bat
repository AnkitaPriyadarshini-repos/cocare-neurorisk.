@echo off
REM CO CARE - start the app on http://localhost:8000
cd /d "%~dp0backend"
python -m pip install -q -r requirements.txt
echo.
echo  CO CARE is running. Open http://localhost:8000 in your browser.
echo  Press Ctrl+C to stop.
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
