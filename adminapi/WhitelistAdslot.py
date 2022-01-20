
from . import adminApi
import time,re
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils, Redis
from utils import UserAuthUtil

@adminApi.post('/whitelistAdslot/import', tags=['Admin-WhiteList AdSlot'],summary="导入包名单AdSlot")
async def importWhitelistAdSlot(req:Request,content:str = Form(...)):
    was = content.split('\n')
    for w in was:
        matchObj = re.match( r'(.*)_(\d+)x(\d+)$', w, re.M|re.I)
        if len(matchObj.groups()) == 3:
            pn = matchObj.group(1)
            width = matchObj.group(2)
            height = matchObj.group(3)
            price = 0
            RWhitelistAdSlot.create(was_bundle=pn,was_width=width,was_height=height, was_price = price)
        print("\r\n")
    return Func.jsonResult({"result":True})


@adminApi.post('/whitelistAdslot/export', tags=['Admin-WhiteList AdSlot'],summary="导入包名单AdSlot")
async def importWhitelistAdSlot(req:Request):
    result = ""
    _was = RWhitelistAdSlot.select().where(RWhitelistAdSlot.was_status == 1).dicts()
    for _wa in _was:
        result = result + "{0}\"{1}\",\"{2}\",\"{3}\",\"{4}\"{5},\n".format("{",_wa['was_bundle'],str(_wa['was_width']),str(_wa['was_height']) ,str(_wa['was_price']) ,"}")
    return Func.jsonResult({"result":result})