from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.RModel import *
from common import Func, Utils
from utils import UserAuthUtil


@adminApi.post('/order/save', tags=['Admin-Order'],summary="新增/编辑Order")
async def save(req:Request,orderId:int = Form(0), orderName:str=Form(...), orderCode:str=Form(''), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    try:
        if orderId > 0:
            ROrder.update(o_name = orderName, o_code = orderCode).where(ROrder.o_id == orderId).execute()
        else:
            order = ROrder.create(o_name = orderName, o_code = orderCode, o_status=1, o_create_time=int(time.time()))
            orderId = order.o_id
        return Func.jsonResult({"orderId":orderId})
    except Exception as e:
        return Func.jsonResult({"orderId":orderId},"发生错误，出现冲突", 100000500)


@adminApi.get('/order/list', tags=['Admin-Order'],summary="Order列表")
async def orderList(page: int = Query(1), pageSize: int = Query(20), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    orders = ROrder.select().where(ROrder.o_status == 1).order_by(ROrder.o_id.desc()).paginate(page, pageSize).dicts()
    totalCount = ROrder.select().where(ROrder.o_status == 1).count()
    orderList = []
    for order in orders:
        orderList.append({
                "orderId":order['o_id'],
                "orderName":order['o_name'],
                "orderCode":order['o_code']
            })
    dt = {"orderList": orderList}
    page_info = Func.outputPageInfo(page, pageSize, totalCount)
    dt = {**dt, **page_info}
    return Func.jsonResult(dt)


@adminApi.delete('/order/remove', tags=['Admin-Order'],summary="删除Order")
async def remove(orderId:int = Query(...,description="OrderID"), signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    ROrder.update(o_status = 0).where(ROrder.o_id == orderId).execute()
    return Func.jsonResult({"orderId":orderId},"order removed")
