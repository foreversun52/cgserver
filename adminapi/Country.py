'''
Descripttion: 
version: 
Author: WGQ
Date: 2021-11-11 14:40:28
LastEditors: WGQ
LastEditTime: 2021-11-12 17:58:46
'''

from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil


@adminApi.post('/country/save', tags=['Admin-Country'],summary="新增/编辑Country")
async def save(req:Request,countryId:int = Form(0),countryName:str=Form(...),countryCode3:str=Form(...),countryCode2:str=Form(...),countryTimezoneUtc:int=Form(...),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if countryId > 0:
            RCountry.update(c_name = countryName,c_code3 = countryCode3,c_code2 = countryCode2, c_timezone_utc = countryTimezoneUtc ).where(RCountry.c_id == countryId).execute()
        else:
            cty = RCountry.create(c_name = countryName, c_code3 =  countryCode3,c_code2 = countryCode2, c_timezone_utc = countryTimezoneUtc )
            countryId = cty.c_id
        return Func.jsonResult({"countryId":countryId})
    except Exception as e:
        return Func.jsonResult({"countryId":countryId},"发生错误，出现冲突",100000500)

@adminApi.get('/country/list', tags=['Admin-Country'],summary="Country列表")
async def countryList(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    countries = RCountry.select().where(RCountry.c_status == 1).order_by(RCountry.c_id.desc()).dicts()
    countryList = []
    for _country in countries:
        countryList.append({
                "countryId":_country['c_id'],
                "countryName":_country['c_name'],
                "countryCode3":_country['c_code3'],
                "countryCode2":_country['c_code2'],
                "countryTimezoneUtc":_country['c_timezone_utc'],
            })
    return Func.jsonResult({"countryList":countryList})

@adminApi.delete('/country/remove', tags=['Admin-Country'],summary="删除Country")
async def remove(countryId:int = Query(...,description="CountryID"), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RCountry.update(c_status = 0).where(RCountry.c_id == countryId).execute()
    return Func.jsonResult({"countryId":countryId},"adx removed")
