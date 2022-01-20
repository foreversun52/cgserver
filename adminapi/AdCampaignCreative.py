'''
Descripttion: 
version: 
Author: WGQ
Date: 2021-11-06 20:33:36
LastEditors: WGQ
LastEditTime: 2021-11-14 21:07:57
'''

from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil

@adminApi.post('/adCampaignCreative/save', tags=['Admin-Creative'],summary="新增/编辑adCampaignCreative")
async def save(req:Request,adCampaignCreativeId:int = Form(0),
                adCampaignId:int = Form(0),
                adCampaignCreativeName:str=Form(...),
                adCampaignCreativeRemark:str=Form(...),
                adCampaignCreativeBidMaxPrice:float = Form(...),
                adCampaignCreativeHeight:float = Form(...),
                adCampaignCreativeWidth:float = Form(...),
                adCampaignCreativeUrl: str = Form(...),
                adCampaignCreativeType:str = Form(...),
                adCampaignCreativeExt:str = Form(""), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    if adCampaignCreativeExt == "":
        adCampaignCreativeExt = "{}"
    if adCampaignCreativeId > 0:
        RAdCampaignCreative.update(
            acc_name = adCampaignCreativeName,
            acc_remark = adCampaignCreativeRemark,
            acc_bid_max_price  = adCampaignCreativeBidMaxPrice,
            acc_height = adCampaignCreativeHeight,
            acc_width = adCampaignCreativeWidth,
            acc_url = adCampaignCreativeUrl,
            acc_type = adCampaignCreativeType,
            acc_ext = adCampaignCreativeExt
        ).where(RAdCampaignCreative.acc_id == adCampaignCreativeId).execute()
    else:
        adCampaignCreative = RAdCampaignCreative.create(
            acc_ac_id = adCampaignId, acc_name = adCampaignCreativeName,
            acc_remark = adCampaignCreativeRemark,
            acc_bid_max_price  = adCampaignCreativeBidMaxPrice,
            acc_height = adCampaignCreativeHeight,
            acc_width = adCampaignCreativeWidth,
            acc_url = adCampaignCreativeUrl,
            acc_type = adCampaignCreativeType,
            acc_ext = adCampaignCreativeExt,
            ac_create_time = int(time.time()))
        adCampaignCreativeId = adCampaignCreative.acc_id
    return Func.jsonResult({"adCampaignCreativeId":adCampaignCreativeId})

@adminApi.get('/adCampaignCreative/list', tags=['Admin-Creative'],summary="adCampaignCreative列表")
async def adCampaignCreativeList(adCampaignId:int = Query(...), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    accs = RAdCampaignCreative.select().where(RAdCampaignCreative.acc_status == 1, RAdCampaignCreative.acc_ac_id == adCampaignId).order_by(RAdCampaignCreative.acc_id.desc()).dicts()
    adCampaignCreativeList = []
    for _adCampaignCreative in accs:
        adCampaignCreativeList.append({
                "adCampaignId":_adCampaignCreative['acc_ac_id'],
                "adCampaignCreativeId":_adCampaignCreative['acc_id'],
                "adCampaignCreativeName":_adCampaignCreative['acc_name'],
                "adCampaignCreativeRemark":_adCampaignCreative['acc_remark'],
                "adCampaignCreativeBidMaxPrice":_adCampaignCreative['acc_bid_max_price'],
                "adCampaignCreativeHeight":_adCampaignCreative['acc_height'],
                "adCampaignCreativeWidth":_adCampaignCreative['acc_width'],
                "adCampaignCreativeUrl":_adCampaignCreative['acc_url'],
                "adCampaignCreativeStatus":_adCampaignCreative['acc_status'],
                "adCampaignCreativeType":_adCampaignCreative['acc_type'],
                "adCampaignCreativeExt":_adCampaignCreative['acc_ext'],
            })
    return Func.jsonResult({"adCampaignCreativeList":adCampaignCreativeList})

@adminApi.delete('/adCampaignCreative/remove', tags=['Admin-Creative'],summary="删除adCampaignCreative")
async def remove(adCampaignCreativeId:int = Query(...,description="adCampaignCreativeID"),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RAdCampaignCreative.update(acc_status = 0).where(RAdCampaignCreative.acc_id == adCampaignCreativeId).execute()
    return Func.jsonResult({"adCampaignCreativeId":adCampaignCreativeId},"adCampaignCreative removed")


@adminApi.get('/adCampaignCreative/video/profile', tags=['Admin-Creative'],summary="AdCampaignCreative Video Profile")
async def videoProfile(adCampaignCreativeId:int = Query(...,description="adCampaignCreativeID"),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RAdExchange.update(acc_status = 0).where(RAdExchange.acc_id == adCampaignCreativeId).execute()
    return Func.jsonResult({"adCampaignCreativeId":adCampaignCreativeId},"adCampaignCreative removed")