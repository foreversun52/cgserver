'''
Descripttion: 
version: 
Author: WGQ
Date: 2021-11-06 08:54:33
LastEditors: WGQ
LastEditTime: 2021-11-06 09:20:42
'''
from model.CModel import *
from common import Func
pwd = "123456"
pwdSalt = Func.md5(Func.randomStr(20))
encPwd = Func.md5(pwd + pwdSalt)

CSystemAdmin.create(sa_username = "forever", sa_password = encPwd, sa_password_salt = pwdSalt)