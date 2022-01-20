# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：PostBackDataCountUtil.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/11/26 15:59 
'''
import boto3, time

def athenaQuery(sql):
    S3_KEY = "AKIA4P3WFQJIJNSYQMT6"
    S3_SECRET = "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"
    S3_BUCKET = "lzdlog"
    s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'), region_name='ap-southeast-1',
                      aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    athena = boto3.client('athena', region_name='ap-southeast-1', aws_access_key_id=S3_KEY,
                          aws_secret_access_key=S3_SECRET)
    s3_output = "s3://lzdlog/queryresult/"
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={
            'Database': 'lazada_rtb_v2'
        },
        ResultConfiguration={
            'OutputLocation': s3_output
        }
    )
    file_name = response['QueryExecutionId'] + '.csv'
    key = "queryresult/" + file_name
    return_data = {'status': False, 'data': '', 'msg': 'success'}
    for i in range(15):
        try:
            time.sleep(1)
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)['Body'].read().decode("utf-8")
            return_data['status'] = True
            return_data['data'] = obj
            return return_data
        except Exception as e:
            return_data['msg'] = e
            # return return_data
    else:
        return_data['msg'] = 'no data'
        return return_data