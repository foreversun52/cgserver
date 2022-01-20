'''
Descripttion:
version:
Author: WGQ
Date: 2021-11-06 20:31:49
LastEditors: WGQ
LastEditTime: 2021-11-16 14:38:51
'''

from common.Redis import getRedis
from . import adminApi
import time,json
from fastapi import Query, Depends, Body, Form,Request, File, UploadFile
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils, Redis
from utils import UserAuthUtil, AdCampaignUtil
import csv

@adminApi.post('/adCampaign/save', tags=['Admin-Campaign'],summary="新增/编辑adCampaign")
async def save(req:Request,
               adCampaignId:int = Form(...),
               adCampaignName:str=Form(...),
               adCampaignCountryId:int=Form(...),
               adCampaignOrderId:int=Form(...),
               adCampaignDeeplink:str=Form(...),
               adCampaignClickUrl:str=Form(...),
               adCampaignPreAuditClickUrl:str=Form(""),
               adCampaignImpressionTrackingUrl:str=Form(...),
               adCampaignClickTrackingUrl:str=Form(...),
               adCampaignTypeId:str=Form(...),
               adCampaignStartDate:int=Form(0),
               adCampaignEndDate:int=Form(0),
               adCampaignMemberId:str=Form(...),
               adCampaignPriority:str=Form(...),
               adCampaignRemark:str=Form(""),
               signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    if adCampaignEndDate != 0:
        adCampaignEndDate = int(adCampaignEndDate/1000) + 86399
    if adCampaignId > 0:
        RAdCampaign.update(ac_name = adCampaignName,
                            ac_c_id = adCampaignCountryId,
                            ac_o_id = adCampaignOrderId,
                            ac_deeplink = adCampaignDeeplink,
                            ac_click_url = adCampaignClickUrl,
                            ac_impression_tracking_url = adCampaignImpressionTrackingUrl,
                            ac_ct_id = adCampaignTypeId,
                            ac_click_tracking_url = adCampaignClickTrackingUrl,
                            ac_member_id = adCampaignMemberId,
                            ac_valid_start_time  = int(adCampaignStartDate/1000),
                            ac_valid_end_time  = adCampaignEndDate,
                            ac_priority = adCampaignPriority,
                            ac_remark = adCampaignRemark).where(RAdCampaign.ac_id == adCampaignId).execute()
    else:
        adCampaign = RAdCampaign.create(ac_name = adCampaignName,
                            ac_c_id = adCampaignCountryId,
                            ac_o_id = adCampaignOrderId,
                            ac_deeplink = adCampaignDeeplink,
                            ac_click_url = adCampaignClickUrl,
                            ac_impression_tracking_url = adCampaignImpressionTrackingUrl,
                            ac_ct_id = adCampaignTypeId,
                            ac_click_tracking_url = adCampaignClickTrackingUrl,
                            ac_member_id = adCampaignMemberId,
                            ac_status = 1,
                            ac_valid_start_time  = adCampaignStartDate,
                            ac_valid_end_time  = adCampaignEndDate,
                            ac_priority = adCampaignPriority,
                            ac_create_time = int(time.time()),
                            ac_remark = adCampaignRemark)
        adCampaignId = adCampaign.ac_id
    return Func.jsonResult({"adCampaignId":adCampaignId})

@adminApi.get('/adCampaign/list', tags=['Admin-Campaign'],summary="adCampaign列表")
async def adCampaignList(countryId :int = Query(0), orderId :int = Query(0), page:int = Query(1),pageSize:int = Query(20), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    _where = RAdCampaign.ac_status.in_([1,2])
    if countryId > 0:
        _where = _where & (RAdCampaign.ac_c_id == countryId)
    if orderId > 0:
        _where = _where & (RAdCampaign.ac_o_id == orderId)
    acs = RAdCampaign.select(RAdCampaign,RCountry, ROrder).join(ROrder, JOIN.LEFT_OUTER, on = (ROrder.o_id == RAdCampaign.ac_o_id)).join(RCountry, JOIN.LEFT_OUTER, on = (RCountry.c_id == RAdCampaign.ac_c_id)).where(_where).order_by(RAdCampaign.ac_id.desc()).paginate(page,pageSize).dicts()

    campaigns = []
    for _ac in acs:
        campaigns.append({
                    "adCampaignId":_ac["ac_id"],
                    "adCampaignCountryName":_ac["c_name"],
                    "adCampaignCountryId":_ac["ac_c_id"],
                    "adCampaignOrderId":_ac["ac_o_id"],
                    "adCampaignOrderName":_ac["o_name"],
                    "adCampaignName":_ac["ac_name"],
                    "adCampaignMemberId":_ac["ac_member_id"],
                    "adCampaignTypeId":_ac["ac_ct_id"],
                    # "adCampaignStatusString":_ac["ac_status_name"],
                    "adCampaignStatus":str(_ac["ac_status"]),
                    # "adCampaignValidDate":_ac["ac_valid_date"],
                    "adCampaignDeeplink":_ac["ac_deeplink"],
                    "adCampaignClickUrl":_ac["ac_click_url"],
                    "adCampaignImpressionTrackingUrl":_ac["ac_impression_tracking_url"],
                    "adCampaignClickTrackingUrl":_ac["ac_click_tracking_url"],
                    "adCampaignStartDate":_ac["ac_valid_start_time"]*1000,
                    "adCampaignEndDate":_ac["ac_valid_end_time"]*1000,
                    "adCampaignPriority":_ac["ac_priority"],
                    "adCampaignRemark":_ac["ac_remark"],
                })
    totalCount = RAdCampaign.select().where(_where).count()
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**{"adCampaignList":campaigns}, **page_info}
    return Func.jsonResult(dt)

@adminApi.delete('/adCampaign/remove', tags=['Admin-Campaign'],summary="删除adCampaign")
async def remove(adCampaignId:int = Query(...,description="adCampaignID"),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RAdCampaign.update(ac_status = 0).where(RAdCampaign.ac_id == adCampaignId).execute()
    return Func.jsonResult({"adCampaignId":adCampaignId},"adCampaign removed")


@adminApi.post('/adCampaign/import', tags=['Admin-Campaign'], summary='上传CampaignList')
async def importCampaign(file:UploadFile = File(...)):
    campaigns = []
    with open("tmp/temp.csv",'wb+') as f:
        f.write(file.file.read())
        f.close()
    with open('tmp/temp.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        idx = 0
        for row in reader:
            if idx > 0:
                campaigns.append({
                    "adCampaignName":row[0] +"/"+ row[1],
                    "adCampaignMemberId":row[2],
                    "adCampaignId":row[3],
                    "adCampaignType":row[4],
                    "adCampaignStatusString":row[5],
                    "adCampaignValidDate":row[6],
                    "adCampaignDeeplink":row[7],
                    "adCampaignClickUrl":row[8],
                    "adCampaignImpressionTrackingUrl":row[9],
                    "adCampaignClickTrackingUrl":row[10],
                })
            idx += 1
    return Func.jsonResult({"adCampaignList":campaigns})

@adminApi.post('/adCampaign/batchSave', tags=['Admin-Campaign'], summary='上传CampaignList')
async def importCampaign(countryId:int = Form(...), orderId:int = Form(...), adCampaignList:str = Form(...),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    adCampaigns = json.loads(adCampaignList)
    for adCampaign in adCampaigns:
        flag = AdCampaignUtil.checkUrl(countryId, adCampaign["adCampaignClickUrl"])
        if not flag:
            return Func.jsonResult({}, "country error")
    for adCampaign in adCampaigns:
        if RAdCampaign.get_or_none(RAdCampaign.ac_id == adCampaign["adCampaignId"]) is not None:
            RAdCampaign.update(ac_id = adCampaign["adCampaignId"],
                                ac_c_id = countryId,
                                ac_o_id = orderId,
                                ac_name = adCampaign["adCampaignName"],
                                ac_member_id = adCampaign["adCampaignMemberId"],
                                # ac_campaign_type = adCampaign["adCampaignType"],
                                # ac_status_name = adCampaign["adCampaignStatusString"],
                                # ac_valid_date = adCampaign["adCampaignValidDate"],
                                ac_deeplink = adCampaign["adCampaignDeeplink"],
                                ac_click_url = adCampaign["adCampaignClickUrl"],
                                ac_impression_tracking_url = adCampaign["adCampaignImpressionTrackingUrl"],
                                ac_click_tracking_url = adCampaign["adCampaignClickTrackingUrl"]).where(RAdCampaign.ac_id == adCampaign["adCampaignId"]).execute()
        else:
            RAdCampaign.create(ac_id = adCampaign["adCampaignId"],
                                ac_c_id = countryId,
                                ac_o_id = orderId,
                                ac_name = adCampaign["adCampaignName"],
                                ac_member_id = adCampaign["adCampaignMemberId"],
                                # ac_campaign_type = adCampaign["adCampaignType"],
                                # ac_status_name = adCampaign["adCampaignStatusString"],
                                ac_valid_date = adCampaign["adCampaignValidDate"],
                                ac_deeplink = adCampaign["adCampaignDeeplink"],
                                ac_click_url = adCampaign["adCampaignClickUrl"],
                                ac_impression_tracking_url = adCampaign["adCampaignImpressionTrackingUrl"],
                                ac_click_tracking_url = adCampaign["adCampaignClickTrackingUrl"])
    return Func.jsonResult({})


@adminApi.post('/adCampaign/switch', tags=['Admin-Campaign'],summary="同步到Redis")
async def syncToRedis(adCampaignId:int = Form(...), adCampaignStatus:int = Form(...), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    RAdCampaign.update(ac_status = adCampaignStatus).where(RAdCampaign.ac_id == adCampaignId).execute()
    return Func.jsonResult({"adCampaignId":adCampaignId},"Switched")


@adminApi.post('/adCampaign/syncToRedis', tags=['Admin-Campaign'],summary="同步到Redis")
async def syncToRedis(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    rds = Redis.getRedis()
    countries = RCountry.select().dicts()
    for country in countries:
        _adCampaigns =  RAdCampaign.select().where(RAdCampaign.ac_status == 1,RAdCampaign.ac_c_id == country["c_id"]).dicts()
        adCampaigns = []
        for _ac in _adCampaigns:
            ac = {
                "adCampaignId":_ac["ac_id"],
                "adCampaignClickUrl":_ac["ac_click_url"],
                "adCampaignDeeplink":_ac["ac_deeplink"],
                "adCampaignClickTrackingUrl":_ac["ac_click_tracking_url"],
                "adCampaignImpressTrackingUrl":_ac["ac_impression_tracking_url"]
            }
            _adCampainAndCreatives = RAdCampaignCreative.select(RAdCampaignCreative).where(RAdCampaignCreative.acc_ac_id == _ac["ac_id"], RAdCampaignCreative.acc_status == 1).dicts()
            adCampainAndCreatives = []
            for _acc in _adCampainAndCreatives:
                adCampainAndCreatives.append({
                    "adCampaignCreativeId":_acc["acc_id"],
                    "adCampaignCreativeType":_acc["acc_type"],
                    "adCampaignCreativeUrl":_acc["acc_url"],
                    "adCampaignCreativeWidth":_acc["acc_width"],
                    "adCampaignCreativeHeight":_acc["acc_height"],
                    "adCampaignBidMaxPrice":_acc["acc_bid_max_price"],
                })
            ac["adCampaignCreativeList"] = adCampainAndCreatives
            adCampaigns.append(ac)
            # rds.hset("LZD:AdCampaignHash:"+country["c_code3"],_ac["ac_id"],json.dumps(ac))
            # 需要把两位国家和三位国家码都要放进来
        rds.set("LZD:AdCampaignList:"+country["c_code3"],json.dumps(adCampaigns))
    return Func.jsonResult({},"Synced")