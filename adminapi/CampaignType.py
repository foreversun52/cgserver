# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：campaignType.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/12/2 17:32 
'''
from . import adminApi
import time
from datetime import datetime
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil

@adminApi.get('/campaignType/list', tags=['Admin-campaignType'],summary="campaignType列表")
async def campaignTypeList(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    campaigns = RCampaignType.select().where(RCampaignType.ct_status == 1).order_by(RCampaignType.ct_id.desc()).dicts()
    _campaignTypeList = []
    for campaign in campaigns:
        _campaignTypeList.append({
                "campaignId":campaign['ct_id'],
                "campaignName":campaign['ct_name'],
                "campaignCode":campaign['ct_code']
            })
    return Func.jsonResult({"campaignTypeList":_campaignTypeList})