REM @echo off

REM Skip build if both zip files exist
IF NOT EXIST "tmp\" (
    MKDIR "tmp"
    GOTO StartBuild
)

IF EXIST "tmp\scrapy.zip" (
    IF EXIST "tmp\layer.zip" (
        ECHO Skip build
        GOTO EndBuild
    )
)

:StartBuild

REM Build Docker image if either of the zip files does not exist
cd lambda_layer
CALL build.bat
cd ..

:EndBuild

copy /y source\Learn\Transform.py tmp\Transform.py

REM Initialize Terraform
cd terraform
terraform init

REM Apply Terraform save state
terraform apply -auto-approve



cd ..