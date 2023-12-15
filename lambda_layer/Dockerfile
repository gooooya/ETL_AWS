# Use Amazon Linux 2 image
FROM amazonlinux:2

# Install required build tools and libraries
RUN yum update -y
RUN yum groupinstall -y "Development Tools"
RUN yum install -y gcc gcc-c++ libffi-devel zlib-devel bzip2-devel epel-release openssl11 openssl11-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel

# Download Python 3.11 source code
RUN curl -O https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz

# Extract and compile Python source
RUN tar -xf Python-3.11.0.tgz
WORKDIR /Python-3.11.0
RUN CFLAGS=$(pkg-config --cflags openssl11) \
    LDFLAGS=$(pkg-config --libs openssl11) \
    ./configure --enable-optimizations --with-ensurepip=install --with-openssl11
RUN make altinstall

# Clean up the tar file and source directory
WORKDIR /
RUN rm Python-3.11.0.tgz
RUN rm -rf /Python-3.11.0

WORKDIR /app

# Set PATH environment variable
ENV PATH="/app/python/bin:$PATH"
ENV PYTHONPATH="/app/python:$PYTHONPATH"
ENV MY_S3_BUCKET_NAME="my-scrapy-output"
# Upgrade pip for Python 3.11
RUN python3.11 -m pip install --upgrade pip

# Install required Python packages
RUN python3.11 -m pip install scrapy boto3 -t /app/python

# create scrapy project
RUN scrapy startproject suumo

# COPY handle
COPY tmp/my_scrapy.py suumo/suumo/spiders

# Package the installed libraries into a zip file
RUN cd /app && zip -r layer.zip python/
RUN zip -r scrapy.zip suumo/