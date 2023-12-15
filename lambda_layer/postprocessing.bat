@echo off
SET FOLDER_PATH=tmp

IF EXIST "%FOLDER_PATH%" (
    rd /S /Q "%FOLDER_PATH%"
    echo Delete folder: %FOLDER_PATH%
)