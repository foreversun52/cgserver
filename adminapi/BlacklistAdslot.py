
from . import adminApi
import time, os, zipfile
from fastapi import Query, Depends, Body, Form, Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func
from utils import UserAuthUtil
from starlette.responses import FileResponse
import json


@adminApi.get('/blacklistAdslot/list', tags=['Admin-BlackListAdSlot'], summary="包名单AdSlot列表")
async def blacklistAdSlotList(req: Request, page: int = Query(1), pageSize: int = Query(20), countryId:int = Query(0), adxId:int = Query(0), Bundle:str = Query(''), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _where = (RBlacklistAdSlot.bas_status == 1)
    if countryId != 0:
        _where &= (RBlacklistAdSlotCountryAdxRelation.bascar_c_id == countryId)
    if adxId != 0:
        _where &= (RBlacklistAdSlotCountryAdxRelation.bascar_ae_id == adxId)
    if Bundle != '':
        _where &= (RBlacklistAdSlot.bas_bundle.contains(Bundle))
    _bascars = RBlacklistAdSlot.select(RBlacklistAdSlot, RBlacklistAdSlotCountryAdxRelation).join(RBlacklistAdSlotCountryAdxRelation, JOIN.LEFT_OUTER, on=(
                RBlacklistAdSlot.bas_id == RBlacklistAdSlotCountryAdxRelation.bascar_bas_id)).where(_where).order_by(
        RBlacklistAdSlot.bas_id.desc(), RBlacklistAdSlotCountryAdxRelation.bascar_id.desc()).paginate(page, pageSize).dicts()
    totalCount = RBlacklistAdSlot.select(RBlacklistAdSlot, RBlacklistAdSlotCountryAdxRelation).join(
        RBlacklistAdSlotCountryAdxRelation, JOIN.LEFT_OUTER, on=(RBlacklistAdSlot.bas_id == RBlacklistAdSlotCountryAdxRelation.bascar_bas_id)).where(_where).count()
    blacklistAdSlotCountryAdxRelations = []
    for _bascar in _bascars:
        if _bascar['bascar_id'] and _bascar['bascar_status'] == 0:
            totalCount -= 1
            continue
        blacklistAdSlotCountryAdxRelations.append({
            "blacklistAdSlotCountryAdxRelationId": _bascar['bascar_id'],
            "blacklistAdSlotId": _bascar['bas_id'],
            "blacklistAdSlotBundle": _bascar['bas_bundle'],
            "blacklistAdSlotWidth": _bascar['bas_width'],
            "blacklistAdSlotHeight": _bascar['bas_height'],
            "blacklistAdSlotCountryId": _bascar['bascar_c_id'],
            "blacklistAdSlotAdxId": _bascar['bascar_ae_id'],
        })
    dt = {"blacklistAdSlotCountryAdxRelations": blacklistAdSlotCountryAdxRelations}
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**dt, **page_info}
    return Func.jsonResult(dt)


@adminApi.post('/blacklistAdslot/save', tags=['Admin-BlackListAdSlot'], summary="新增/编辑BlackListAdSlot")
async def save(req: Request, blacklistAdSlotId: int = Form(0), blacklistAdSlotBundle: str = Form(...), countryAdx:str=Form(...), blacklistAdSlotWidth: str = Form(...), blacklistAdSlotHeight: str = Form(...), blacklistAdSlotStatus: int = Form(1), blacklistAdSlotAdExchangeId: int = Form(0), blacklistAdSlotCountryId: int = Form(0), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if blacklistAdSlotId > 0:
            RBlacklistAdSlot.update(bas_bundle=blacklistAdSlotBundle, bas_width=blacklistAdSlotWidth, bas_height=blacklistAdSlotHeight, bas_status=blacklistAdSlotStatus).where(RBlacklistAdSlot.bas_id == blacklistAdSlotId).execute()
        else:
            bas = RBlacklistAdSlot.create(bas_bundle=blacklistAdSlotBundle, bas_width=blacklistAdSlotWidth, bas_height=blacklistAdSlotHeight,
                                          bas_status=blacklistAdSlotStatus)
            blacklistAdSlotId = bas.bas_id
        countryAdxList = json.loads(countryAdx)
        for countryAdx in countryAdxList:
            Adxs = countryAdx.get('countryAdxList')
            if len(Adxs) > 0:
                bascars = RBlacklistAdSlotCountryAdxRelation.select().where(
                    RBlacklistAdSlotCountryAdxRelation.bascar_bas_id == blacklistAdSlotId,
                    RBlacklistAdSlotCountryAdxRelation.bascar_c_id == countryAdx.get("countryId"))
                for bascar in bascars:
                    if bascar.bascar_ae_id in Adxs:
                        bascar.bascar_status = 1
                        bascar.save()
                        Adxs.remove(bascar.bascar_ae_id)
                    else:
                        bascar.bascar_status = 0
                        bascar.save()
                for adx in Adxs:
                    RBlacklistAdSlotCountryAdxRelation.create(bascar_bas_id=blacklistAdSlotId,
                                                           bascar_c_id=countryAdx.get("countryId"), bascar_ae_id=adx,
                                                           bascar_status=1, bascar_create_time=int(time.time()))
            else:
                RBlacklistAdSlotCountryAdxRelation.update(bascar_status=0).where(
                    RBlacklistAdSlotCountryAdxRelation.bascar_bas_id == blacklistAdSlotId,
                    RBlacklistAdSlotCountryAdxRelation.bascar_c_id == countryAdx.get("countryId")).execute()
        return Func.jsonResult({"blacklistAdSlotId": blacklistAdSlotId})
    except Exception as e:
        print(e)
        return Func.jsonResult({"blacklistAdSlotId": blacklistAdSlotId}, "发生错误，出现冲突", 100000500)


@adminApi.delete('/blacklistAdslot/remove', tags=['Admin-BlackListAdSlot'], summary="删除BlackListAdSlot")
async def remove(blacklistAdSlotId: int = Query(..., description="black list AdSlot Id"), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RBlacklistAdSlot.update(bas_status=0).where(
        RBlacklistAdSlot.bas_id == blacklistAdSlotId).execute()
    RBlacklistAdSlotCountryAdxRelation.update(bascar_status=0).where(RBlacklistAdSlotCountryAdxRelation.bascar_bas_id==blacklistAdSlotId).execute()
    return Func.jsonResult({"blacklistAdSlotId": blacklistAdSlotId}, "blacklist Ad Slot Removed")


@adminApi.get('/blacklistAdslot/countryAdx/list', tags=['Admin-BlackListAdSlot'],summary="BlackListAdSlotCountry对应Adx列表")
async def blacklistAdSlotList(signInUser: dict = Depends(UserAuthUtil.verifyToken), blacklistAdSlotId:int = Query(0)):
    countries = RCountry.select().where(RCountry.c_status == 1).order_by(RCountry.c_id.desc()).dicts()
    blacklistAdSlotCountryAdxList = []
    for _country in countries:
        blacklistAdSlotCountryAdxRelationList = RBlacklistAdSlotCountryAdxRelation.select().where(RBlacklistAdSlotCountryAdxRelation.bascar_bas_id==blacklistAdSlotId,
            RBlacklistAdSlotCountryAdxRelation.bascar_status == 1, RBlacklistAdSlotCountryAdxRelation.bascar_c_id==_country['c_id']).dicts()
        countryAdxList = []

        if len(blacklistAdSlotCountryAdxRelationList) > 0:
            for blacklistAdSlotCountryAdxRelation in blacklistAdSlotCountryAdxRelationList:
                countryAdxList.append(blacklistAdSlotCountryAdxRelation['bascar_ae_id'])

        blacklistAdSlotCountryAdxList.append({
            "countryId": _country['c_id'],
            "countryName": _country['c_name'],
            "countryCode3": _country['c_code3'],
            "countryCode2": _country['c_code2'],
            "countryTimezoneUtc": _country['c_timezone_utc'],
            'countryAdxList':countryAdxList
        })
    return Func.jsonResult({"blacklistAdSlotCountryAdxList":blacklistAdSlotCountryAdxList})


@adminApi.get('/blacklistAdslot/export', tags=['Admin-BlackListAdSlot'], summary="BlackListAdSlot Export")
async def export(req: Request):
    countries = RCountry.select().where(RCountry.c_status == 1).order_by(RCountry.c_id.desc()).dicts()
    adxs = RAdExchange.select().where(RAdExchange.ae_status == 1).order_by(RAdExchange.ae_id.desc()).dicts()
    exportPath = os.path.join(os.getcwd(), "export")
    if not os.path.exists(exportPath):
        os.mkdir(exportPath)
    jsonPath = os.path.join(exportPath, "json")
    if not os.path.exists(jsonPath):
        os.mkdir(jsonPath)
    blacklistAdSlotPath = os.path.join(jsonPath, "blacklistAdSlot")
    if not os.path.exists(blacklistAdSlotPath):
        os.mkdir(blacklistAdSlotPath)
    zipPath = os.path.join(exportPath, "zip")
    if not os.path.exists(zipPath):
        os.mkdir(zipPath)
    for country in countries:
        for adx in adxs:
            name = f"{country.get('c_code3')}_{adx.get('ae_name')}"
            fileName = f"{name}.json"
            _where = (RBlacklistAdSlotCountryAdxRelation.bascar_status == 1)
            _where &= (RBlacklistAdSlot.bas_status == 1)
            _where &= (RBlacklistAdSlotCountryAdxRelation.bascar_c_id == country.get("c_id"))
            _where &= (RBlacklistAdSlotCountryAdxRelation.bascar_ae_id == adx.get("ae_id"))
            bascars = RBlacklistAdSlotCountryAdxRelation.select(RBlacklistAdSlotCountryAdxRelation, RBlacklistAdSlot).join(RBlacklistAdSlot, on=(RBlacklistAdSlot.bas_id==RBlacklistAdSlotCountryAdxRelation.bascar_bas_id)).order_by(RBlacklistAdSlot.bas_id.desc()).where(_where).dicts()
            data = {}
            if len(bascars) > 0:
                for bascar in bascars:
                    key = f"{name}_{bascar.get('bas_bundle')}_{bascar.get('bas_width')}x{bascar.get('bas_height')}"
                    data[key] = 1
            filePath = os.path.join(blacklistAdSlotPath, fileName)
            with open(filePath, "w") as fw:
                fw.write(json.dumps(data))
    if not os.path.exists(exportPath):
        os.mkdir(exportPath)
    zipFilePath = os.path.join(zipPath, "blacklistAdSlot.zip")
    zip = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(blacklistAdSlotPath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fPath = path.replace(blacklistAdSlotPath, 'blacklistAdSlot')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fPath, filename))
    zip.close()
    return FileResponse(zipFilePath, filename="blacklistAdSlot.zip")
