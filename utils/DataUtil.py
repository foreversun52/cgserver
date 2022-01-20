# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：DataUtil.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/11/17 20:45 
'''
import io
import os
from datetime import datetime, timezone, timedelta

import boto3, time
from dateutil import tz


def pk_2_utc(time_str, from_timezone, to_timezone):
    timezone_dict = {"utc": "UTC", "sg": "Asia/Singapore", "vn": "Asia/Ho_Chi_Minh", "cn": "Asia/Shanghai", "th": "Asia/Bangkok", "ph": "Asia/Manila"}

    naive_time = datetime.strptime(time_str, '%Y-%m-%d %H')

    from_time = naive_time.astimezone(tz=tz.gettz(timezone_dict.get(from_timezone)))

    to_time = from_time.astimezone(tz=tz.gettz(timezone_dict.get(to_timezone)))

    return to_time


def athenaQuery(sql,database):
    S3_KEY = "AKIA4P3WFQJIJNSYQMT6"
    S3_SECRET = "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"
    S3_BUCKET = "lzdlog"
    s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'), region_name='ap-southeast-1', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    athena = boto3.client('athena', region_name='ap-southeast-1', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    s3_output = "s3://lzdlog/queryresult/"
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': s3_output
        }
    )
    return response['QueryExecutionId']
    # file_name = response['QueryExecutionId'] + '.csv'
    # return file_name
    # key = "queryresult/" + file_name
    # return_data = {'status': False, 'file_path': '', 'msg': 'success'}
    # for i in range(60):
    #     try:
    #         time.sleep(1)
    #         file_path = os.path.join(os.getcwd(), "csvoutput", "csv", file_name)
    #         obj = s3.get_object(Bucket=S3_BUCKET, Key=key)['Body'].read().decode("utf-8")
    #         _file = open(file_path, "w+")
    #         _file.write(obj)
    #         return_data['status'] = True
    #         return_data['file_path'] = file_path
    #         return return_data
    #     except Exception as e:
    #         return_data['msg'] = e
    #         # return return_data
    # else:
    #     return_data['msg'] = 'no data'
    #     return return_data
