'''
Descripttion: 
version: 
Author: WGQ
Date: 2021-11-06 20:16:50
LastEditors: WGQ
LastEditTime: 2021-11-17 10:43:28
'''

from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil



@adminApi.post('/adx/save', tags=['Admin-Adx'],summary="新增/编辑ADX")
async def save(req:Request,adxId:int = Form(0),adxName:str=Form(...),adxCode:str=Form(...),adxRemark:str=Form(''),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if adxId > 0:
            RAdExchange.update(ae_name = adxName,ae_remark = adxRemark, ae_code = adxCode).where(RAdExchange.ae_id == adxId).execute()
        else:
            adx = RAdExchange.create(ae_name = adxName,ae_remark = adxRemark, ae_code = adxCode)
            adxId = adx.ae_id
        return Func.jsonResult({"adxId":adxId})
    except Exception as e:
        return Func.jsonResult({"adxId":adxId},"发生错误"+str(e),10000500)

@adminApi.get('/adx/list', tags=['Admin-Adx'],summary="ADX列表")
async def adxList(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    sas = RAdExchange.select().where(RAdExchange.ae_status == 1).order_by(RAdExchange.ae_id.desc()).dicts()
    systemAdmins = []
    for _adx in sas:
        systemAdmins.append({
                "adxId":_adx['ae_id'],
                "adxName":_adx['ae_name'],
                "adxCode":_adx['ae_code'],
                "adxRemark":_adx['ae_remark'],
            })
    return Func.jsonResult({"adxList":systemAdmins})

@adminApi.delete('/adx/remove', tags=['Admin-Adx'],summary="删除ADX")
async def remove(adxId:int = Query(...,description="ADXID"),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RAdExchange.update(ae_status = 0).where(RAdExchange.ae_id == adxId).execute()
    return Func.jsonResult({"adxId":adxId},"adx removed")
