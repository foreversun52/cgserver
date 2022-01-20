'''
@Descripttion:
@version:
@Author: WGQ
@Date: 2020-05-26 15:07:25
LastEditors: WGQ
LastEditTime: 2020-12-25 17:50:25
'''
import time
from fastapi import HTTPException, Form,Header
from common.Config import app_config
from itsdangerous import JSONWebSignatureSerializer

async def verifyToken(usertoken: str=Header(...)):
    """ 验证token """
    try:
        s = JSONWebSignatureSerializer(app_config.JWT_SECRET)
        if s is None or usertoken == "":
            raise HTTPException(status_code=401, detail='verify token failed',
                                headers={'X-Error': "There goes my error"})
        new_data  = s.loads(usertoken)
        if new_data is None or new_data == {}:
            raise HTTPException(status_code=401, detail='verify token failed',
                                headers={'X-Error': "There goes my error"})
        else:
            return new_data
    except Exception as e:
        raise HTTPException(status_code=401, detail='verify token failed',
                                headers={'X-Error': "There goes my error"})

async def makeToken():
    pass