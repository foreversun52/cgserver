FROM python:3.7.9-alpine3.12
ADD . /data/server
WORKDIR /data/server
RUN echo http://mirrors.ustc.edu.cn/alpine/v3.12/main > /etc/apk/repositories && \
    echo http://mirrors.ustc.edu.cn/alpine/v3.12/community >> /etc/apk/repositories
# RUN echo -e 'http://mirrors.tuna.tsinghua.edu.cn/alpine/v3.12/main/\nhttp://mirrors.tuna.tsinghua.edu.cn/alpine/v3.12/community/' > /etc/apk/repositories
RUN apk update && apk upgrade
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev libxml2 libxml2-dev nano
RUN apk --update add libxml2-dev libxslt-dev musl-dev libgcc openssl-dev curl build-base alpine-sdk
RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev libsndfile-dev
RUN export C_INCLUDE_PATH=/usr/include/libxml2/

RUN apk add --no-cache python3-dev libstdc++ && \
    apk add --no-cache g++ && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# RUN apk add python3-dev
# RUN mkdir $HOME/.pip/
# ADD pip.conf $HOME/.pip/pip.conf
# COPY ./pip.conf $HOME/.pip/
RUN pip install https://github.com/kpu/kenlm/archive/master.zip
RUN pip install -r ./requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
EXPOSE 3091
ENV RUN_ENV=dev
# CMD ['sh','run.sh']
CMD ["sh","run.sh"]
