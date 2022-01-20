# -*- coding: UTF-8 -*-
'''
@Project ：driftingbottleserver 
@File    ：WechatMiniAppUtil.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/7/14 16:07 
'''
import requests
from common import Redis
from common.Config import app_config

def getAccessToken():
    """获取服务号的AccessToken"""
    cacheKey = "wechat_access_token_" + app_config.WECHAT_APPID
    redis = Redis.getRedis()
    if redis.get(cacheKey) is None:
        payload = {
            'grant_type': 'client_credential',
            'appid': app_config.WECHAT_APPID,
            'secret': app_config.WECHAT_APPSECRET
        }
        # atUrl  = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(current_app.config["WECHAT_APPID"],current_app.config["WECHAT_APPSECRET"])

        req = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=payload, timeout=3, verify=False)
        access_token = str(req.json().get('access_token'))
        redis.set(cacheKey,access_token)
        redis.expire(cacheKey,6000)
    else:
        access_token = str(redis.get(cacheKey),encoding="utf-8")
    return access_token