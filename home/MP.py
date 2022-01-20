# -*- coding: UTF-8 -*-
'''
@Project ：cgserver 
@File    ：MP.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2022/1/19 17:34 
'''
import hashlib
from . import home
from fastapi import Response, Request, Query
from common.Config import app_config


@home.get('/mp/callback', tags=['微信公众号'], summary='消息回调和处理')
async def mpcallback(req: Request, signature :str=Query(''), timestamp:str=Query(''), nonce:str=Query(''), echostr:str=Query('')):
    try:
        token = app_config.WECHAT_TOKEN
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr
        else:
            return ""
    except Exception as e:
        return e