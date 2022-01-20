# -*- coding: UTF-8 -*-
'''
@Project ：cgserver 
@File    ：MP.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2022/1/19 17:34 
'''
from . import home
from fastapi import Response, Request


@home.get('/mp/callback', tags=['微信公众号'], summary='消息回调和处理')
async def mpcallback(req: Request):
    pass