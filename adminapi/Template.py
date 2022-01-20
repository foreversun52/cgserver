
from . import adminApi
import time
from fastapi import Query, Depends, Body, Form, Request, Response
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils, Redis
from utils import UserAuthUtil


@adminApi.get('/adtemplate/list', tags=['Admin-Template'], summary="AdTemplate List")
async def whitelistAdSlotList(req: Request, page: int = Query(1), pageSize: int = Query(20), type:int=Query(0), orderId:int = Query(0), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _where = (RAdTemplate.at_status == 1)
    if type > 0:
        _where &= (RAdTemplate.at_type == type)
    if orderId > 0:
        _where &= (RAdTemplate.at_o_id == orderId)
    _bas = RAdTemplate.select(RAdTemplate, ROrder).join(ROrder, JOIN.LEFT_OUTER, on=(ROrder.o_id == RAdTemplate.at_o_id)).where(_where).paginate(page, pageSize).dicts()
    totalCount = RAdTemplate.select().where(_where).count()
    bas = []
    for _ba in _bas:
        bas.append({
            "adTemplateId": _ba.get("at_id"),
            "adTemplateName": _ba.get("at_name"),
            "adTemplateFileName": _ba.get("at_filename"),
            "adTemplateCode": _ba.get("at_code"),
            "adTemplateOrderId": _ba.get("at_o_id"),
            "adTemplateOrderName": _ba.get("o_name"),
            "adTemplateContent": _ba.get("at_content"),
            "adTemplateType": _ba.get("at_type"),
            "adTemplateStatus": _ba.get("at_status"),
            "adTemplateRemark": _ba.get("at_remark"),
            "adTemplateCreateTime": _ba.get("at_create_time")
        })
    dt = {"adTemplates": bas}
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**dt, **page_info}
    return Func.jsonResult(dt)


@adminApi.post('/adtemplate/save', tags=['Admin-Template'], summary="Save Ad Template")
async def save(req: Request, adTemplateId: int = Form(0), adTemplateOrderId: int = Form(0), adTemplateName: str = Form(...), adTemplateFileName: str = Form(...), adTemplateCode: str = Form(...), adTemplateContent: str = Form(...), adTemplateType: str = Form(...), adTemplateRemark: str = Form(""), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    if adTemplateId > 0:
        RAdTemplate.update(at_name=adTemplateName, at_filename=adTemplateFileName, at_code=adTemplateCode, at_content=adTemplateContent,
                            at_type=adTemplateType, at_remark=adTemplateRemark, at_status=1, at_o_id = adTemplateOrderId).where(RAdTemplate.at_id == adTemplateId).execute()
    else:
        ba = RAdTemplate.create(at_name=adTemplateName, at_filename=adTemplateFileName, at_code=adTemplateCode, at_content=adTemplateContent,
                                at_type=adTemplateType, at_remark=adTemplateRemark, at_status=1, at_o_id = adTemplateOrderId, at_create_time=int(time.time()))
        adTemplateId = ba.at_id
    return Func.jsonResult({"adTemplateId": adTemplateId})

@adminApi.post('/adtemplate/download', tags=['Admin-Template'], summary="Download Ad Template Html")
async def save(req: Request, adTemplateId: int = Form(0)):
    adTemplate = RAdTemplate.get(RAdTemplate.at_id == adTemplateId)
    if adTemplate is None:
        return Func.jsonResult({},"template not found",100000404)
    else:
        return Response(content=adTemplate.at_content, media_type="text/html", headers={"Content-Disposition": "attachment; filename="+adTemplate.at_filename})

@adminApi.delete('/adtemplate/remove', tags=['Admin-Template'], summary="Remove Ad Template")
async def remove(adTemplateId: int = Form(0), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RAdTemplate.update(at_status=0).where(
        RAdTemplate.at_id == adTemplateId).execute()
    return Func.jsonResult({"AdTemplateId": adTemplateId}, "Whitelist App Removed")
