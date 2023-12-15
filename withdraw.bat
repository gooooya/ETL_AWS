REM save bucket
REM aws s3 sync s3://my-common-output buckup_data

REM delete bucket
aws s3 rm s3://my-common-output --recursive

@echo off
SET BUCKET=my-common-output
SETLOCAL ENABLEDELAYEDEXPANSION

REM Check if AWS CLI is available
aws --version >nul 2>&1
IF NOT "%ERRORLEVEL%" == "0" (
    echo AWS CLI is not installed or not in PATH.
    exit /b
)

REM Delete all objects recursively
aws s3 rm s3://%BUCKET% --recursive

REM If versioning is enabled, we need to delete the versions and markers
aws s3api list-object-versions --bucket %BUCKET% --query "DeleteMarkers[].{Key: Key, VersionId: VersionId}" --output text | for /f "tokens=1,2" %%a in ('more') do (
    aws s3api delete-object --bucket %BUCKET% --key "%%a" --version-id "%%b"
)

aws s3api list-object-versions --bucket %BUCKET% --query "Versions[].{Key: Key, VersionId: VersionId}" --output text | for /f "tokens=1,2" %%a in ('more') do (
    aws s3api delete-object --bucket %BUCKET% --key "%%a" --version-id "%%b"
)

echo All objects and versions deleted from the bucket !BUCKET!.
ENDLOCAL


REM destroy
cd terraform
terraform destroy --auto-approve

cd ..