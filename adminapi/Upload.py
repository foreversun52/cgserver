'''
Descripttion: 
version: 
Author: WGQ
Date: 2020-08-31 09:43:36
LastEditors: WGQ
LastEditTime: 2021-11-11 15:13:00
'''

from . import adminApi
from fastapi import Query, File, UploadFile
import datetime
import os
from common import Func, AliyunOss
import boto3


@adminApi.post('/upload', tags=['上传'], summary='上传图片')
async def uploadImg(file:UploadFile = File(...)):
    # s3 user name: s3upload; access key: AKIA4P3WFQJIORXPFWUQ; access secret: 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 region: ap-southeast-1
    cloudfrontPrefix = "https://d1z7ukdmm4qvz5.cloudfront.net/"
    img_url = ""
    # if file is not None:
    #     ossPath = "workapp/" + datetime.datetime.today().strftime('%Y%m%d')+"/quotation/"+Func.md5(Func.randomStr(20))+".jpg"
    #     imgUrl = ""
    #     dt = AliyunOss.upload(ossPath,file)
    #     if dt.get("result") == True:
    #         img_url = dt.get("file_url")
    S3_KEY = "AKIA4P3WFQJIORXPFWUQ"
    S3_SECRET = "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"
    S3_BUCKET = "cbrtbstatic"
    image = file.filename
    filename, file_extension = os.path.splitext(image)
    s3_filestore_path = 'images/' + datetime.datetime.today().strftime('%Y%m%d')+"/static/"+Func.md5(Func.randomStr(20)) + file_extension
    content_type_dict = {".png": "image/png", ".html": "text/html",
                            ".css": "text/css", ".js": "application/javascript",
                            ".jpg": "image/png", ".gif": "image/gif",
                            ".jpeg": "image/jpeg", ".mp4": "video/mp4",
                            ".avi":"video/avi", ".mkv":"video/x-matroska",
                            ".wmv":"video/x-ms-wmv",".ogg":"video/ogg", ".webm":"video/webm"}

    content_type = content_type_dict[file_extension]
    s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'), region_name='ap-southeast-1', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    s3.put_object(Body=file.file, Bucket=S3_BUCKET, Key=s3_filestore_path, ContentType=content_type, ACL='public-read')
    return Func.jsonResult({"file_url": cloudfrontPrefix + s3_filestore_path})
