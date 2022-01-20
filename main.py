# -*- coding: utf-8 -*-
# coding=utf-8
'''
Descripttion:
version:
Author: WGQ
Date: 2020-12-25 10:23:28
LastEditors: WGQ
LastEditTime: 2021-11-11 17:32:32
'''
# !/usr/bin/python -u
import codecs
import time,os
import sys
import logging
from fastapi import FastAPI, Depends, Header, HTTPException, Request,Query
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from model.CModel import database

from common.Config import app_config
from adminapi import adminApi
from home import home
from api import api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playhouse.shortcuts import model_to_dict
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

app = FastAPI(title='Forever Server', description='Forever Server', version='3.0')

@app.on_event('startup')
def init_scheduler():
    scheduler = AsyncIOScheduler()
    # 开发模式不开启
    if app_config.DEBUG == False:
        print('开启定时任务')
    else:
        print('开发模式不开启定时任务')
    scheduler.start()

async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def manage_db(request: Request, call_next):
    try:
        if database.is_closed():
            database.connect()
        response = await call_next(request)
        return response
    except Exception as e:
        print(e)
    finally:
        if not database.is_closed():
            database.close()

# 挂载静态文件，指定目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(adminApi, prefix='/adminapi', responses={404: {'description': 'NOT FOUND'}})
app.include_router(home, prefix='', responses={404: {'description': 'NOT FOUND'}})
app.include_router(api, prefix='/api', responses={404: {'description': 'NOT FOUND'}})

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

if __name__ == '__main__':
    uvicorn.run('main:app', reload=app_config.DEBUG, host='0.0.0.0', port=app_config.PORT)