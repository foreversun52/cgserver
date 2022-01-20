# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：impressionType.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/12/2 17:25 
'''
from . import adminApi
import time
from datetime import datetime
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil

@adminApi.get('/impression_type/list', tags=['Admin-impressionType'],summary="impressionType列表")
async def impressionTypeList(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    impressions = RImpressionType.select().where(RImpressionType.it_status == 1).order_by(RImpressionType.it_id.desc()).dicts()
    _impressionTypeList = []
    for impression in impressions:
        _impressionTypeList.append({
                "impressionId":impression['it_id'],
                "impressionName":impression['it_name'],
                "impressionCode":impression['it_code']
            })
    return Func.jsonResult({"impressionTypeList":_impressionTypeList})