# -*- coding: UTF-8 -*-
'''
@Project ：server
@File    ：UpdateLinkPeewee.py
@IDE     ：PyCharm
@Author  ：Forever
@Date    ：2021/5/14 18:04
'''
from model.SWOModel import SwoSystemAdmin
import requests
from common.Config import app_config

def updateLink():
    SwoSystemAdmin.select().where(SwoSystemAdmin.sa_status == 1).dicts()
    requests.get("http://0.0.0.0:"+str(app_config.PORT)+"/pluginapi/ping")
