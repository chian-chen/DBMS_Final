FROM mysql:8.0-debian
ENV MYSQL_ROOT_PASSWORD=password\
    MYSQL_DATABASE=test

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential wget libmysqlclient-dev libgmp3-dev python3-pip libssl-dev libffi-dev python3-dev

# FROM python:3.9.9
WORKDIR /mysqludf
COPY ./ .
# RUN pip3 install ftfy regex tqdm torch torchvision --break-system-packages
RUN pip3 install ftfy regex tqdm scikit-image opencv-python lpips torch torchvision --break-system-packages
RUN apt-get install -y git
RUN pip3 install git+https://github.com/openai/CLIP.git --break-system-packages
# RUN g++ avg_big_num.cpp -fPIC -lgmp -shared -o /usr/lib/mysql/plugin/big_average.so -I /usr/include/mysql