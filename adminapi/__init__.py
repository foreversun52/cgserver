'''
@Descripttion: 
@version: 
@Author: WGQ
@Date: 2020-05-26 15:07:25
LastEditors: WGQ
LastEditTime: 2021-11-14 21:21:06
'''
from fastapi import APIRouter

adminApi = APIRouter()

from . import Auth, SystemAdmin