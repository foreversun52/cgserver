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
from fastapi.responses import HTMLResponse
from fastapi import Response, Request, Query
from common.Config import app_config


@home.get('/mp/callback', tags=['微信公众号'], summary='消息回调和处理')
async def mpcallback(req: Request, signature:str=Query(''), timestamp:str=Query(''), nonce:str=Query(''), echostr:str=Query('')):
    _ = "".join(sorted([app_config.WECHAT_TOKEN, timestamp, nonce]))
    sign = hashlib.sha1(_.encode('UTF-8')).hexdigest()
    return HTMLResponse(content=echostr if sign == signature else "error")