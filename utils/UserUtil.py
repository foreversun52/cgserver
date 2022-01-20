'''
@Descripttion: 
@version: 
@Author: WGQ
@Date: 2020-02-25 22:17:19
@LastEditors: WGQ
@LastEditTime: 2020-04-23 18:10:18
'''
from model.RModel import *

def apiReturnUserProfile(user_id):
    '''
        返回给客户端的标准用户信息包装
    '''
    user = RUser.get_by_id(user_id)

    birthday = user.u_birthday
    if birthday == '':
        birthday = "2000-01-01"
    nickname = user.u_nickname
    if nickname == "":
        nickname = user.u_username
    rt_user = {
        "user_id": user.u_id,
        "user_username": user.u_username,
    }

    return rt_user

def getUserIdByWechatUnionId(wechat_union_id):
    user = RUser.get_or_none(RUser.u_wechat_union_id == wechat_union_id)
    if user is None:
        return 0
    else:
        return user.u_id

def createUser():
    pass