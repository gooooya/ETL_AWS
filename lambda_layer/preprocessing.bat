REM Start Docker daemon
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

REM Wait start Docker
:waitloop
timeout /t 5 >nul
docker version >nul 2>&1
if errorlevel 1 goto waitloop

REM Copy in docker context
set SOURCE_FILE=..\Scrapy\scrapytest\scrapytest\spiders\my_scrapy.py
set DEST_DIR=tmp

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

copy "%SOURCE_FILE%" "%DEST_DIR%"

REM error check
if %ERRORLEVEL% neq 0 (
    echo coppy error
    exit /b %ERRORLEVEL%
)
