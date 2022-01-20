# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：Report.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/12/2 15:10 
'''
from . import adminApi
import time
from datetime import datetime
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil

@adminApi.get('/report/list', tags=['Admin-Report'],summary="Report列表")
async def reportList(country:str=Query(''), impression:str=Query(''), campaign_type:str=Query(''), start_date:str=Query(''), end_date:str=Query(''), app_bundle:str=Query(''),adx:str=Query(''), page:int = Query(1),pageSize:int = Query(20), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    if start_date != '':
        date = start_date.split('T')[0].split('-')
        start_year = int(date[0])
        start_month = int(date[1])
        start_day = int(date[2])
        start_time = start_date.split('T')[1].split(':')
        start_hour = int(start_time[0])
        _date = end_date.split('T')[0].split('-')
        end_year = int(_date[0])
        end_month = int(_date[1])
        end_day = int(_date[2])
        end_time = end_date.split('T')[1].split(':')
        end_hour = int(end_time[0])
        _where = (RBidReport.br_year >= start_year) & (RBidReport.br_year <= end_year)
        _where &= (RBidReport.br_month >= start_month) & (RBidReport.br_month <= end_month)
        _where &= (RBidReport.br_day >= start_day) & (RBidReport.br_day <= end_day)
        _where &= (RBidReport.br_hour >= start_hour) & (RBidReport.br_hour <= end_hour)
    else:
        timeStamp = int(time.time())
        timeArray = datetime.utcfromtimestamp(timeStamp)
        year = timeArray.year
        month = timeArray.month
        day = timeArray.day
        _where = (RBidReport.br_year==year) & (RBidReport.br_month==month) & (RBidReport.br_day == day)
    if app_bundle:
        _where &= (RBidReport.br_app_bundle.contains(app_bundle))
    if country:
        _where &= (RBidReport.br_c_id==country)
    if impression:
        _where &= (RBidReport.br_it_id==impression)
    if campaign_type:
        _where &= (RBidReport.br_ct_id==campaign_type)
    if adx:
        _where &= (RBidReport.br_ae_id==adx)
    reports = RBidReport.select(RBidReport, RCountry, RCampaignType, RAdExchange, RImpressionType).where(_where).join(RCountry, JOIN.LEFT_OUTER, on=(RBidReport.br_c_id==RCountry.c_id)).join(RImpressionType, JOIN.LEFT_OUTER, on=(RBidReport.br_it_id==RImpressionType.it_id)).join(RCampaignType, JOIN.LEFT_OUTER, on=(RBidReport.br_ct_id==RCampaignType.ct_id)).join(RAdExchange, JOIN.LEFT_OUTER, on=(RBidReport.br_ae_id==RAdExchange.ae_id)).order_by(RBidReport.br_hour.desc()).paginate(page,pageSize).dicts()
    totalCount = RBidReport.select().where(_where).count()
    reportList = []
    if len(reports) > 0:
        for report in reports:
            reportList.append({
                "reportId":report.get("br_id"),
                # "reportYear":report.get("br_year"),
                # "reportMonth":report.get("br_month"),
                # "reportDay":report.get("br_day"),
                "reportDate":f"{report.get('br_year')}-{report.get('br_month')}-{report.get('br_day')}",
                "reportHour":f"{str(report.get('br_hour'))} h",
                "reportCountry":report.get("c_name"),
                "reportAdx":report.get("ae_name"),
                "reportAppBundle":report.get("br_app_bundle"),
                "reportCampaignType":report.get("ct_name"),
                "reportBidCount":report.get("br_bid_count"),
                "reportImpCount":report.get("br_imp_count"),
                "reportClickCount":report.get("br_click_count"),
                "reportPostbackCount":report.get("br_postback_count"),
                "reportCost":report.get("br_cost"),
                "reportImpressionType":report.get("it_name"),
            })
    dt = {"reportList": reportList}
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**dt, **page_info}
    return Func.jsonResult(dt)
