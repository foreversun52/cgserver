# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：AdCampaignUtil.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2022/1/11 18:20 
'''
from purl import URL
from model.RModel import RCountry

def checkUrl(countryId, url):
    country = RCountry.get_or_none(RCountry.c_id == countryId)
    country = country.c_code3
    domain = URL(url).domain()
    aDomain = ""
    if country == "IDN":
        aDomain = "lazada.co.id"
    if country == "SGP":
        aDomain = "lazada.sg"
    if country == "MYS":
        aDomain = "lazada.com.my"
    if country == "PHL":
        aDomain = "lazada.com.ph"
    if country == "THA":
        aDomain = "lazada.co.th"
    if country == "VNM":
        aDomain = "lazada.vn"
    if aDomain in domain:
        return True
    else:
        return False