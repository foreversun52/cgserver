
from . import adminApi
import time
from fastapi import Query, Depends, Body, Form,Request
from playhouse.shortcuts import model_to_dict
from model.CModel import *
from common import Func, Utils
from utils import UserAuthUtil

@adminApi.get('/systemadmin/profile', tags=['后台API-管理员'], summary='管理员信息')
async def userProfile(userId:int = Query(0),signInUser = Depends(UserAuthUtil.verifyToken)):
    if userId == 0:
        userId = signInUser.get("admin_id")
    print(userId)
    print(signInUser)
    _user = CSystemAdmin.get_or_none(CSystemAdmin.sa_id == userId)
    if _user is not None:
        _user = model_to_dict(_user)
        user = {
            "systemAdminId":userId,
            "systemAdminName":_user.get("sa_username")
        }
        return Func.jsonResult({"user":user})
    else:
        return Func.jsonResult({},"user not found",200000404)


@adminApi.post('/admin/save', tags=['Admin-管理员'],summary="新增/编辑管理员")
async def save(req:Request,sa_id:int = Form(0),sa_username:str=Form(...),sa_password:str=Form(...),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    pwdSalt = Func.md5(Func.randomStr(20))
    pwdEncrypted = Func.md5(sa_password + pwdSalt)
    if sa_id > 0:
        CSystemAdmin.update(sa_username = sa_username,sa_password = pwdEncrypted,sa_password_salt = pwdSalt).where(CSystemAdmin.sa_id == sa_id).execute()
    else:
        if sa_username == '':
            return Func.jsonResult({},"用户名不能为空",100000500)
        elif CSystemAdmin.get_or_none(CSystemAdmin.sa_username == sa_username) is not None:
            return Func.jsonResult({},"用户名已存在，请采用其他的",100000500)
        else:
            sa = CSystemAdmin.create(sa_username = sa_username,sa_password = pwdEncrypted,sa_password_salt = pwdSalt)
            sa_id = sa.sa_id
    return Func.jsonResult({"systemAdminId":sa_id})

@adminApi.get('/admin/list', tags=['Admin-管理员'],summary="管理员列表")
async def adminList(signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    sas = CSystemAdmin.select().where(CSystemAdmin.sa_status == 1).order_by(CSystemAdmin.sa_id.desc()).dicts()
    systemAdmins = []
    for sa in sas:
        systemAdmins.append(sa)
    return Func.jsonResult({"systemAdmins":systemAdmins})

@adminApi.delete('/admin/remove', tags=['Admin-管理员'],summary="删除管理员")
async def remove(system_admin_id:int = Query(...,description="管理员ID"),signInUser: dict = Depends(UserAuthUtil.verifyToken)):
    CSystemAdmin.update(sa_status = 0).where(CSystemAdmin.sa_id == system_admin_id).execute()
    return Func.jsonResult({"systemAdminId":system_admin_id},"system admin removed")
