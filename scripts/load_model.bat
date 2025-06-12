@echo off

@REM Load environment variables from .env file
set MODEL_NAME=skyllama
set MODEL_VERSION=1.0
for /f "usebackq tokens=1,2 delims==" %%A in (".env") do set %%A=%%B

@REM Check if the model is already loaded and remove it if it exists
ollama list | findstr /i "%MODEL_NAME%:%MODEL_VERSION%" >nul
if %errorlevel% equ 0 (
    echo "Removing existing model '%MODEL_NAME%:%MODEL_VERSION%'..."
    ollama rm %MODEL_NAME%:%MODEL_VERSION%
)

echo "Loading model '%MODEL_NAME%:%MODEL_VERSION%' from Modelfile..."
ollama create %MODEL_NAME%:%MODEL_VERSION% -f Modelfile
