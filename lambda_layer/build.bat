call preprocessing.bat

REM Build the Docker image using the provided Dockerfile
docker build --no-cache -t lambda-layer-updated .

REM Run a container from the built image
for /f "tokens=*" %%i in ('docker run -d lambda-layer-updated /bin/true') do set container_id=%%i

REM Copy layer.zip from the container to the host machine
docker cp %container_id%:/app/layer.zip ../tmp/layer.zip
docker cp %container_id%:/app/scrapy.zip ../tmp/scrapy.zip

REM Stop and remove
docker rm -f %container_id%
call postprocessing.bat