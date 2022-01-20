'''
Descripttion: 
version: 
Author: WGQ
Date: 2021-11-12 16:13:21
LastEditors: WGQ
LastEditTime: 2021-11-14 22:39:14
'''

from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils, Redis
from utils import UserAuthUtil

@adminApi.post('/whitelistApp/list', tags=['Admin-WhiteList AdSlot'],summary="导入包名单AdSlot")
async def whitelistAdSlotList(req:Request,page:int = Query(1),pageSize:int = Query(20), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _bas = RWhitelistApp.select().where(RWhitelistApp.was_status == 1).dicts()
    bas = []
    for _ba in _bas:
        bas.append(_ba)
    totalCount = RWhitelistApp.select().where(RWhitelistApp.was_status == 1).count()
    dt = {"whitelistAdSlots": bas}
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**dt, **page_info}
    return Func.jsonResult({"whitelistAdSlots":bas})

@adminApi.post('/whitelistApp/save', tags=['Admin-WhiteList AdSlot'],summary="新增/编辑Country")
async def save(req:Request,whitelistAppId:int = Form(0),whitelistAppName:str=Form(...),whitelistAppBundle:str=Form(...), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if whitelistAppId > 0:
            RWhitelistApp.update(wa_name = whitelistAppName, wa_bundle = whitelistAppBundle).where(RWhitelistApp.wa_id == whitelistAppId).execute()
        else:
            ba = RWhitelistApp.create(wa_name = whitelistAppName, wa_bundle = whitelistAppBundle, wa_createtime = int(time.time()))
            whitelistAppId = ba.wa_id
        return Func.jsonResult({"whitelistAppId":whitelistAppId})
    except Exception as e:
        return Func.jsonResult({"whitelistAppId":whitelistAppId},"发生错误，出现冲突",100000500)

@adminApi.get('/whitelistApp/list', tags=['Admin-WhiteList AdSlot'],summary="Country列表")
async def whitelistAppList(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _whiteListApps = RWhitelistApp.select().where(RWhitelistApp.wa_status == 1).order_by(RWhitelistApp.wa_id.desc()).dicts()
    whiteListApps = []
    for _ba in _whiteListApps:
        whiteListApps.append({
                "whitelistAppId":_ba['wa_id'],
                "whitelistAppName":_ba['wa_name'],
                "whitelistAppBundle":_ba['wa_bundle'],
                "whitelistAppCreateTime":_ba['wa_createtime']
            })
    return Func.jsonResult({"whitelistAppList":whiteListApps})

@adminApi.delete('/whitelistApp/remove', tags=['Admin-WhiteList AdSlot'],summary="删除Country")
async def remove(whitelistAppId:int = Query(...,description="Whitelist App Id"), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RWhitelistApp.update(wa_status = 0).where(RWhitelistApp.wa_id == whitelistAppId).execute()
    return Func.jsonResult({"whitelistAppId":whitelistAppId},"Whitelist App Removed")

@adminApi.post('/whitelistApp/syncToRedis', tags=['Admin-WhiteListApp'],summary="同步到Redis")
async def syncToRedis(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    rds = Redis.getRedis()
    blackListApps = RWhitelistApp.select().where(RWhitelistApp.wa_status == 1).dicts()
    rds.delete("LZD:WhitelistApp")
    for ba in blackListApps:
        rds.sadd("LZD:WhitelistApp",ba["wa_bundle"])
    return Func.jsonResult({},"Whitelist Synced")