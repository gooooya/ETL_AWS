call preprocessing.bat
docker build --no-cache -t myubuntu .
docker run -it my-scrapy-test
call postprocessing.bat