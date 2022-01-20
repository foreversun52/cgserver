'''
Descripttion: 
version: 
Author: WGQ
Date: 2020-11-02 21:14:10
LastEditors: WGQ
LastEditTime: 2021-11-06 09:19:18
'''

from . import adminApi
import time
from fastapi import Query, Depends,Body, Form, Request
from playhouse.shortcuts import model_to_dict
from common import Func, Utils
from utils import UserAuthUtil
from itsdangerous import JSONWebSignatureSerializer
from common.Config import app_config
from model.CModel import *

@adminApi.post('/auth/sign_in', tags=['后台API-验证授权'], summary='登录')
async def signIn(*, request: Request, username: str = Form(...), password: str = Form(...)):
    sa = CSystemAdmin.get_or_none(CSystemAdmin.sa_username == username, CSystemAdmin.sa_status == 1)
    if not sa:
        return Func.jsonResult({},"System Admin Not Found",200000404)
    else:
        # 密码校验
        if sa.sa_password != Func.md5(password + sa.sa_password_salt):
            return Func.makeResult({}, "密码错误", 100000502)
        if sa.sa_status != 1:
            return Func.makeResult({}, "禁止登陆", 100000502)
        sa.sa_signin_time = int(time.time())
        sa.sa_signin_ip = Utils.getClientIp(request,"long")
        jwtUser = {
            "admin_id":sa.sa_id,
            "admin_username":username,
            "iat":int(time.time())
        }
        sa.save()
        s = JSONWebSignatureSerializer(app_config.JWT_SECRET)
        token = s.dumps(jwtUser)
        return Func.jsonResult({'usertoken': token, "username":username})


@adminApi.post('/auth/logout', tags=['后台API-验证授权'], summary='logout')
async def signIn(*, request: Request):
    return Func.jsonResult({})
