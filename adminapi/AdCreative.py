# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：adCreative.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2022/1/6 16:19 
'''
from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil


@adminApi.get('/adcreative/list', tags=['Admin-ad Creative'],summary="AD Creative列表")
async def adCreativeList(page:int = Query(1), pageSize:int = Query(20), type:int=Query(0), orderId:int=Query(0), countryId:int=Query(0), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _where = (RAdCreative.acc_status == 1)
    if type > 0:
        _where &= (RAdCreative.acc_type == type)
    if orderId > 0:
        _where &= (RAdCreative.acc_o_id == orderId)
    if countryId > 0:
        _where &= (RAdCreative.acc_c_id == countryId)
    accs = RAdCreative.select(RAdCreative, RCountry, RAdCreativeVideo, ROrder).join(RAdCreativeVideo, JOIN.LEFT_OUTER, on=(RAdCreativeVideo.accv_acc_id==RAdCreative.acc_id)).join(ROrder, JOIN.LEFT_OUTER, on=(RAdCreative.acc_o_id==ROrder.o_id)).join(RCountry, JOIN.LEFT_OUTER, on=(RAdCreative.acc_c_id==RCountry.c_id)).where(_where).order_by(RAdCreative.acc_id.desc()).paginate(page,pageSize).dicts()
    totalCount = RAdCreative.select().where(_where).count()
    adCreativeList = []
    for acc in accs:
        adCreativeList.append({
                "adCreativeId":acc.get("acc_id"),
                "adCreativeName":acc.get("acc_name"),
                "adCreativeCountryId":acc.get("acc_c_id"),
                "adCreativeOrderId":acc.get("acc_o_id"),
                "adCreativeOrderName":acc.get("o_name"),
                "adCreativeCountryName":acc.get("c_name"),
                "adCreativeUrl":acc.get("acc_url"),
                "adCreativeWidth":acc.get("acc_width"),
                "adCreativeHeight":acc.get("acc_height"),
                "adCreativeStatus":acc.get("acc_status"),
                "adCreativeType":acc.get("acc_type"),
                "adCreativeExt":acc.get("acc_ext"),
                "adCreativeRemark":acc.get("acc_remark"),
                "adCreativeVideoId":acc.get("accv_id") if acc.get("accv_id") else 0,
                "adCreativeVideoTitle":acc.get("accv_title"),
                "adCreativeVideoDescription":acc.get("accv_description"),
                "adCreativeVideoCta":acc.get("accv_cta"),
                "adCreativeVideoDuration":acc.get("accv_duration"),
                "adCreativeVideoIcon":acc.get("accv_icon"),
                "adCreativeVideoCampanionImageUrl":acc.get("accv_campanion_image_url"),

            })
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**{"adCreativeList": adCreativeList}, **page_info}
    return Func.jsonResult(dt)


@adminApi.post('/adcreative/save', tags=['Admin-ad Creative'],summary="新增/编辑ad Creative")
async def save(req:Request, adCreativeId:int=Form(0),adCreativeName:str = Form(''), adCreativeCountryId:int = Form(...),adCreativeOrderId:int = Form(0), adCreativeUrl:str=Form(''), adCreativeWidth:float=Form(0), adCreativeHeight:float=Form(0), adCreativeType:int=Form(1), adCreativeExt:str=Form(''),adCreativeRemark:str=Form(''),adCreativeVideoId:int=Form(0), adCreativeVideoTitle:str=Form(''),adCreativeVideoCta:str=Form(''),adCreativeVideoDescription:str=Form(''),adCreativeVideoDuration:str=Form(''),adCreativeVideoIcon:str=Form(''),adCreativeVideoCampanionImageUrl:str=Form(''), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if adCreativeId > 0:
            RAdCreative.update(acc_name=adCreativeName, acc_c_id=adCreativeCountryId, acc_o_id=adCreativeOrderId, acc_width = adCreativeWidth, acc_height = adCreativeHeight, acc_type=adCreativeType, acc_url=adCreativeUrl, acc_status=1, acc_ext=adCreativeExt, acc_remark=adCreativeRemark).where(RAdCreative.acc_id==adCreativeId).execute()
        else:
            acc = RAdCreative.create(acc_name=adCreativeName, acc_c_id=adCreativeCountryId, acc_o_id=adCreativeOrderId, acc_width = adCreativeWidth, acc_height = adCreativeHeight, acc_type=adCreativeType, acc_url=adCreativeUrl, acc_status=1, acc_ext=adCreativeExt, acc_remark=adCreativeRemark)
            adCreativeId = acc.acc_id
        if adCreativeType == 2:
            if adCreativeVideoId > 0:
                RAdCreativeVideo.update(accv_title=adCreativeVideoTitle, accv_description=adCreativeVideoDescription,
                                         accv_duration=adCreativeVideoDuration, accv_cta=adCreativeVideoCta,
                                         accv_campanion_image_url=adCreativeVideoCampanionImageUrl,
                                         accv_icon=adCreativeVideoIcon, accv_acc_id=adCreativeId).where(RAdCreativeVideo.accv_id==adCreativeVideoId).execute()
            else:
                RAdCreativeVideo.create(accv_title=adCreativeVideoTitle, accv_description=adCreativeVideoDescription, accv_duration=adCreativeVideoDuration, accv_cta=adCreativeVideoCta, accv_campanion_image_url=adCreativeVideoCampanionImageUrl, accv_icon=adCreativeVideoIcon, accv_acc_id=adCreativeId)
        return Func.jsonResult({"adCreativeId": adCreativeId})
    except Exception as e:
        return Func.jsonResult({"adCreativeId":adCreativeId},"发生错误，出现冲突",100000500)