'''
Descripttion: 
version: 
Author: WGQ
Date: 2019-12-26 15:11:22
LastEditors: WGQ
LastEditTime: 2020-08-10 20:26:42
'''
import re

def safeGetInt(params,paramName,defalut_value = 0):
    """ 安全获取params中的int字段 """
    v = params.get(paramName,defalut_value)
    # if type(v) == int:
    #     return v

    if(paramName == ''):
        return defalut_value
    if re.match('^([1-9]\d*|0)(\.\d{1,2})?$',str(v)):
        return int(float(v))
    else:
        return defalut_value

def safeGetFloat(params,paramName,defalut_value = 0):
    """ 安全获取params中的float字段 """
    v  = params.get(paramName,defalut_value)
    if(paramName == ''):
        return defalut_value
    if re.match('^([1-9]\d*|0)(\.\d{1,20})?$',str(v)):
        return float(v)
    else:
        return defalut_value
