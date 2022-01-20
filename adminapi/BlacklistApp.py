'''
Descripttion: 
version: 
Author: WGQ
Date: 2021-11-12 16:13:21
LastEditors: WGQ
LastEditTime: 2021-11-14 22:37:48
'''

from . import adminApi
import time, json, os, zipfile
from fastapi import Query, Depends, Form,Request
from starlette.responses import FileResponse
from model.RModel import *
from common import Func, Redis
from utils import UserAuthUtil
from common.Config import app_config


@adminApi.post('/blacklistApp/save', tags=['Admin-BlackListApp'],summary="新增/编辑Country")
async def save(req:Request,blacklistAppId:int = Form(0),blacklistAppName:str=Form(...),blacklistAppBundle:str=Form(...), countryAdx:str=Form(...), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if blacklistAppId > 0:
            RBlacklistApp.update(ba_name = blacklistAppName, ba_bundle = blacklistAppBundle).where(RBlacklistApp.ba_id == blacklistAppId).execute()
        else:
            ba = RBlacklistApp.create(ba_name = blacklistAppName, ba_bundle = blacklistAppBundle, ba_createtime = int(time.time()))
            blacklistAppId = ba.ba_id
        countryAdxList = json.loads(countryAdx)
        for countryAdx in countryAdxList:
            Adxs = countryAdx.get('countryAdxList')
            if len(Adxs) > 0:
                bacars = RBlacklistAppCountryAdxRelation.select().where(
                    RBlacklistAppCountryAdxRelation.bacar_ba_id == blacklistAppId,
                    RBlacklistAppCountryAdxRelation.bacar_c_id == countryAdx.get("countryId"))
                for bacar in bacars:
                    if bacar.bacar_ae_id in Adxs:
                        bacar.bacar_status = 1
                        bacar.save()
                        Adxs.remove(bacar.bacar_ae_id)
                    else:
                        bacar.bacar_status = 0
                        bacar.save()
                for adx in Adxs:
                    RBlacklistAppCountryAdxRelation.create(bacar_ba_id=blacklistAppId,
                                                            bacar_c_id=countryAdx.get("countryId"), bacar_ae_id=adx,
                                                            bacar_status=1, bacar_create_time=int(time.time()))
            else:
                RBlacklistAppCountryAdxRelation.update(bacar_status=0).where(
                    RBlacklistAppCountryAdxRelation.bacar_ba_id == blacklistAppId,
                    RBlacklistAppCountryAdxRelation.bacar_c_id == countryAdx.get("countryId")).execute()
        return Func.jsonResult({"blacklistAppId":blacklistAppId})
    except Exception as e:
        return Func.jsonResult({"blacklistAppId":blacklistAppId},"发生错误，出现冲突",100000500)


@adminApi.get('/blacklistApp/list', tags=['Admin-BlackListApp'],summary="BlackListApp列表")
async def blacklistAppList(page: int = Query(1), pageSize: int = Query(20), countryId:int = Query(0), adxId:int = Query(0), Bundle:str = Query(''), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _where = (RBlacklistApp.ba_status == 1)
    # _where &= (RBlacklistAppCountryAdxRelation.bacar_status == 1)
    if countryId != 0:
        _where &= (RBlacklistAppCountryAdxRelation.bacar_c_id == countryId)
    if adxId != 0:
        _where &= (RBlacklistAppCountryAdxRelation.bacar_ae_id == adxId)
    if Bundle != '':
        _where &= (RBlacklistApp.ba_bundle.contains(Bundle))
    _bacars = RBlacklistApp.select(RBlacklistApp, RBlacklistAppCountryAdxRelation).join(RBlacklistAppCountryAdxRelation, JOIN.LEFT_OUTER, on=(RBlacklistApp.ba_id == RBlacklistAppCountryAdxRelation.bacar_ba_id)).where(_where).order_by(RBlacklistApp.ba_id.desc(), RBlacklistAppCountryAdxRelation.bacar_id.desc()).paginate(page, pageSize).dicts()
    totalCount = RBlacklistApp.select(RBlacklistApp, RBlacklistAppCountryAdxRelation).join(RBlacklistAppCountryAdxRelation, JOIN.LEFT_OUTER, on=(RBlacklistApp.ba_id == RBlacklistAppCountryAdxRelation.bacar_ba_id)).where(_where).count()
    blackListCountryAdxRelations = []
    for _bacar in _bacars:
        if _bacar['bacar_id'] and _bacar['bacar_status'] == 0:
            totalCount -= 1
            continue
        blackListCountryAdxRelations.append({
                "blackListCountryAdxRelationId":_bacar['bacar_id'],
                "blacklistAppId":_bacar['ba_id'],
                "blacklistAppName":_bacar['ba_name'],
                "blacklistAppBundle":_bacar['ba_bundle'],
                "blacklistAppCountryId":_bacar['bacar_c_id'],
                # "blacklistAppCountryName":_bacar['c_name'],
                "blacklistAppAdxId":_bacar['bacar_ae_id'],
                # "blacklistAppAdxName":_bacar['ae_name']
            })
    dt = {"blackListCountryAdxRelationList": blackListCountryAdxRelations}
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**dt, **page_info}
    return Func.jsonResult(dt)


@adminApi.delete('/blacklistApp/remove', tags=['Admin-BlackListApp'],summary="删除BlackListApp")
async def remove(blacklistAppId:int = Query(...,description="Blacklist App Id"), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RBlacklistApp.update(ba_status = 0).where(RBlacklistApp.ba_id == blacklistAppId).execute()
    RBlacklistAppCountryAdxRelation.update(bacar_status = 0).where(RBlacklistAppCountryAdxRelation.bacar_ba_id == blacklistAppId).execute()
    return Func.jsonResult({"blacklistAppId":blacklistAppId},"Blacklist App Removed")


@adminApi.post('/blacklistApp/syncToRedis', tags=['Admin-BlackListApp'],summary="同步到Redis")
async def syncToRedis(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    rds = Redis.getRedis()
    blackListApps = RBlacklistApp.select().where(RBlacklistApp.ba_status == 1).dicts()
    rds.delete("LZD:BlacklistApp")
    for ba in blackListApps:
        rds.sadd("LZD:BlacklistApp",ba["ba_bundle"])
    return Func.jsonResult({},"Blacklist Synced")


@adminApi.get('/blacklistApp/countryAdx/list', tags=['Admin-BlackListApp'],summary="Country对应Adx列表")
async def blacklistAppList(signInUser: dict = Depends(UserAuthUtil.verifyToken), blacklistAppId:int = Query(0)):
    countries = RCountry.select().where(RCountry.c_status == 1).order_by(RCountry.c_id.desc()).dicts()
    blacklistAppCountryAdxList = []
    for _country in countries:
        blacklistAppCountryAdxRelationList = RBlacklistAppCountryAdxRelation.select().where(RBlacklistAppCountryAdxRelation.bacar_ba_id==blacklistAppId,
            RBlacklistAppCountryAdxRelation.bacar_status == 1, RBlacklistAppCountryAdxRelation.bacar_c_id==_country['c_id']).dicts()
        countryAdxList = []

        if len(blacklistAppCountryAdxRelationList) > 0:
            for blacklistAppCountryAdxRelation in blacklistAppCountryAdxRelationList:
                countryAdxList.append(blacklistAppCountryAdxRelation['bacar_ae_id'])

        blacklistAppCountryAdxList.append({
            "countryId": _country['c_id'],
            "countryName": _country['c_name'],
            "countryCode3": _country['c_code3'],
            "countryCode2": _country['c_code2'],
            "countryTimezoneUtc": _country['c_timezone_utc'],
            'countryAdxList':countryAdxList
        })
    return Func.jsonResult({"blacklistAppCountryAdxList":blacklistAppCountryAdxList})


@adminApi.get('/blacklistApp/export', tags=['Admin-BlackListApp'], summary="BlackListApp Export")
async def export(req: Request):
    countries = RCountry.select().where(RCountry.c_status == 1).order_by(RCountry.c_id.desc()).dicts()
    adxs = RAdExchange.select().where(RAdExchange.ae_status == 1).order_by(RAdExchange.ae_id.desc()).dicts()
    exportPath = os.path.join(os.getcwd(), "export")
    if not os.path.exists(exportPath):
        os.mkdir(exportPath)
    jsonPath = os.path.join(exportPath, "json")
    if not os.path.exists(jsonPath):
        os.mkdir(jsonPath)
    blacklistAppPath = os.path.join(jsonPath, "blacklistApp")
    if not os.path.exists(blacklistAppPath):
        os.mkdir(blacklistAppPath)
    zipPath = os.path.join(exportPath, "zip")
    if not os.path.exists(zipPath):
        os.mkdir(zipPath)
    for country in countries:
        for adx in adxs:
            name = f"{country.get('c_code3')}_{adx.get('ae_name')}"
            fileName = f"{name}.json"
            _where = (RBlacklistAppCountryAdxRelation.bacar_status == 1)
            _where &= (RBlacklistApp.ba_status == 1)
            _where &= (RBlacklistAppCountryAdxRelation.bacar_c_id == country.get("c_id"))
            _where &= (RBlacklistAppCountryAdxRelation.bacar_ae_id == adx.get("ae_id"))
            bacars = RBlacklistAppCountryAdxRelation.select(RBlacklistAppCountryAdxRelation, RBlacklistApp).join(RBlacklistApp, on=(RBlacklistApp.ba_id==RBlacklistAppCountryAdxRelation.bacar_ba_id)).order_by(RBlacklistApp.ba_id.desc()).where(_where).dicts()
            data = {}
            if len(bacars) > 0:
                for bacar in bacars:
                    key = f"{name}_{bacar.get('ba_bundle')}"
                    data[key] = 1
            filePath = os.path.join(blacklistAppPath, fileName)
            with open(filePath, "w") as fw:
                fw.write(json.dumps(data))
    zipFilePath = os.path.join(zipPath, "blacklistApp.zip")
    zip = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(blacklistAppPath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fPath = path.replace(blacklistAppPath, 'blacklistApp')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fPath, filename))
    zip.close()
    return FileResponse(zipFilePath, filename="blacklistApp.zip")