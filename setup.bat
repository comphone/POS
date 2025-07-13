@echo off
echo [1/5] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b
)

echo [2/5] Creating/Verifying Virtual Environment...
if not exist venv ( python -m venv venv )

echo [3/5] Installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b
)

echo [4/5] Setting up database...
if not exist migrations (
    python -m flask --app run db init
    if %errorlevel% neq 0 ( echo ERROR: db init failed. & pause & exit /b )
)

python -m flask --app run db migrate -m "Initial setup"
if %errorlevel% neq 0 ( echo ERROR: db migrate failed. & pause & exit /b )

python -m flask --app run db upgrade
if %errorlevel% neq 0 ( echo ERROR: db upgrade failed. & pause & exit /b )

echo.
echo [5/5] !!!!! SETUP COMPLETE !!!!!
echo.
echo =================================================================
echo NEXT STEP: Create your first user in a NEW command prompt.
echo =================================================================
echo.
pause