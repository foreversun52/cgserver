'''
@Descripttion:
@version:
@Author: WGQ
@Date: 2020-02-11 09:29:01
LastEditors: WGQ
LastEditTime: 2020-10-26 10:55:59
'''
# -*- coding: utf-8 -*-
import oss2
import hashlib
import random
import time
import datetime
from common.Config import app_config

def upload(path = "", file_obj = None):
    """ 阿里云OSS上传Util """
    # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    oss_accessKeyId = "LTAI4Ff4f9v5N5cJ9oUQB1Xh"
    oss_accessKeySecret = "tL4zWW6pKYEsQsskdit594U9UTsGnJ"
    oss_endpoint = app_config.ALIYUNOSS_ENDPOINT
    oss_bucket = "static-xiyiyi"
    auth = oss2.Auth(oss_accessKeyId, oss_accessKeySecret)
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, 'http://' + oss_endpoint, oss_bucket)
    try:
        file = file_obj
    except:
        file = None

    if file is None:
        return {"result": False, "message": "File Not Found", "code": 200000404}
    extName = path.split('.')[-1]
    if extName not in ["jpg", 'jpeg', 'png', 'gif', 'mp3', 'mp4', 'flv', '3gp', 'mpg', 'mpeg', 'wmv']:
        # return Func.makeResult({},"File Type Not Allowed",200000500)
        return {"result": False, "message": "File Type Not Allowed", "code": 200000500}

    m2 = hashlib.md5()
    m2.update((str(random.randrange(10000, 99999)) + str(time.time())).encode("utf8"))
    ossFileName = datetime.datetime.today().strftime('%Y%m%d') + "/" + m2.hexdigest() + "." + extName
    # <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt
    bucket.put_object(path, file)
    file_url = "https://static.xiyiyi.com/" + path
    return {"result": True, "message": "Success", "file_url": file_url, "code": 100000200}
