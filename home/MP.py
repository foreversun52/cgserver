# -*- coding: UTF-8 -*-
'''
@Project ：cgserver 
@File    ：MP.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2022/1/19 17:34 
'''
import hashlib, time, xmltodict
from . import home
from fastapi.responses import HTMLResponse
from fastapi import Response, Request, Query
from common.Config import app_config
from model.CModel import *


@home.get('/mp/callback', tags=['微信公众号'], summary='消息回调和处理')
async def mpcallback(req: Request, signature: str = Query(''), timestamp: str = Query(''), nonce: str = Query(''),
                     echostr: str = Query('')):
    _ = "".join(sorted([app_config.WECHAT_TOKEN, timestamp, nonce]))
    sign = hashlib.sha1(_.encode('UTF-8')).hexdigest()
    return HTMLResponse(content=echostr if sign == signature else "error")


@home.post('/mp/callback', tags=['微信公众号'], summary='消息回调和处理')
async def mpcallback(req: Request):
    try:
        request_body = await req.body()
        data = request_body.decode("utf-8")
        reqObj = xmltodict.parse(data)
        dataObj = reqObj.get("xml")
        fromUserName = dataObj.get("FromUserName")
        toUserName = dataObj.get("ToUserName")
        msgType = dataObj.get("MsgType")
        content = dataObj.get("Content")
        cgs = CCashGift.select().where(CCashGift.cg_name.contains(content)).dicts()
        if msgType == 'text':
            resContent = ""
            if len(cgs) > 0:
                for cg in cgs:
                    remark = cg.get('cg_remark')
                    if not remark:
                        remark = "无"
                    resContent += f"姓名:{cg.get('cg_name')}, 礼金:{cg.get('cg_money')}, 备注:{remark}\n"
            else:
                resContent = f"查无名为:{content} 的送礼人，请检查输入的人名是否正确。"
            XmlForm = f"""<xml>
            <ToUserName><![CDATA[{fromUserName}]]></ToUserName>
            <FromUserName><![CDATA[{toUserName}]]></FromUserName>
            <CreateTime>{time.time()}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{resContent}]]></Content>
            </xml>"""
            return HTMLResponse(content=XmlForm)
    except Exception as e:
        print(e)
    return HTMLResponse(content="success")