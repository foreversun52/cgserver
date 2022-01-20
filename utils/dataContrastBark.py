# -*- coding: UTF-8 -*-
'''
@Project ：dspserver 
@File    ：dataContrast.py
@IDE     ：PyCharm 
@Author  ：Forever
@Date    ：2021/12/27 16:54 
'''
import time, boto3, requests
from io import StringIO
from datetime import datetime
import pandas as pd


def athenaQuery(sql, database):
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
            'Database': database
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


def judge(a, b):
    if a > b:
        a,b = b,a
    if a == 0:
        return (False, 0)
    difference = round((b-a)/a, 2)
    if difference > 0.3:
        return (False, difference)
    return (True, difference)


def splitSql(yearList, monthList, dayList):
    Sql = f"""SELECT bid_month,
               bid_day,
               bid_hour,
               bid_country,
               adx_id,
               sum(bidcount) AS bidcount,
               sum(impCount) AS impCount,
               sum(clickCount) AS clickCount,
               sum(postbackCount) AS postbackCount,
               sum(bid_price * impCount) / 1000.0 AS cost
        FROM
          (SELECT bid_month,
                  bid_day,
                  bid_hour,
                  b.bid_country,
                  adx_id,
                  campaign_type,
                  count(b.bid_id) AS bidcount,
                  sub_type,
                  bid_request.app.bundle AS appbundle,
                  b.imp_width,
                  b.imp_height,
                  count(i.bid_id) AS impCount,
                  count(c.bid_id) AS clickCount,
                  count(p.p_deviceid) AS postbackCount,
                  bid_price
           FROM lazada_rtb_v3.bid_log AS b
           LEFT JOIN
             (SELECT DISTINCT bid_id
              FROM lazada_rtb_v3.impression_log) AS i ON b.bid_id = i.bid_id
           LEFT JOIN
             (SELECT DISTINCT bid_id,
                              device_id
              FROM lazada_rtb_v3.click_log) AS c ON b.bid_id = c.bid_id
           LEFT JOIN
             (SELECT DISTINCT device_id AS p_deviceid,
                              bid_id
              FROM lazada_rtb_v3.post_back_log
              WHERE device_id <> ''
                AND event IN ('first_launch', 'activation')
                AND ((post_back_year = {yearList[0]}
                AND post_back_month = {monthList[0]}
                AND post_back_day = {dayList[0]}) or (post_back_year = {yearList[1]}
                AND post_back_month = {monthList[1]}
                AND post_back_day = {dayList[1]})or (post_back_year = {yearList[2]}
                AND post_back_month = {monthList[2]}
                AND post_back_day = {dayList[2]})) ) AS p ON c.bid_id = p.bid_id
           WHERE (bid_year= {yearList[0]}
             AND bid_month = {monthList[0]}
             AND bid_day  = {dayList[0]}) or (bid_year= {yearList[1]}
             AND bid_month = {monthList[1]}
             AND bid_day  = {dayList[1]})or (bid_year= {yearList[2]}
             AND bid_month = {monthList[2]}
             AND bid_day  = {dayList[2]})
           GROUP BY sub_type,
                    adx_id,
                    bid_request.app.bundle,
                    bid_month,
                    campaign_type,
                    bid_day,
                    bid_hour,
                    bid_price,
                    b.bid_country,
                    b.imp_width,
                    b.imp_height) AS t
        WHERE impCount > 0
        GROUP BY bid_month,
                 bid_day,
                 bid_hour,
               adx_id,
               bid_country"""
    return Sql


def getDate():
    today = int(time.time())
    yesterday = today - 86400
    beforeYesterday = today - 86400 * 2
    todayTimeArray = datetime.utcfromtimestamp(today)
    todayYear = todayTimeArray.year
    todayMonth = todayTimeArray.month
    todayDay = todayTimeArray.day
    yesterdayTimeArray = datetime.utcfromtimestamp(yesterday)
    yesterdayYear = yesterdayTimeArray.year
    yesterdayMonth = yesterdayTimeArray.month
    yesterdayDay = yesterdayTimeArray.day
    beforeYesterdayTimeArray = datetime.utcfromtimestamp(beforeYesterday)
    beforeYesterdayYear = beforeYesterdayTimeArray.year
    beforeYesterdayMonth = beforeYesterdayTimeArray.month
    beforeYesterdayDay = beforeYesterdayTimeArray.day
    yearList = [beforeYesterdayYear, yesterdayYear, todayYear]
    monthList = [beforeYesterdayMonth, yesterdayMonth, todayMonth]
    dayList = [beforeYesterdayDay, yesterdayDay, todayDay]
    beforeOne = today - 3600 * 1
    beforTwo = today - 3600 * 2
    beforeOneTimeArray = datetime.utcfromtimestamp(beforeOne)
    beforeOneHour = beforeOneTimeArray.hour
    beforTwoTimeArray = datetime.utcfromtimestamp(beforTwo)
    beforeTwoHour = beforTwoTimeArray.hour
    hourList = [beforeTwoHour, beforeOneHour]
    return [yearList, monthList, dayList,hourList]


def dataContrast():
    dataList = getDate()
    yearList, monthList, dayList, hourList = dataList[0], dataList[1], dataList[2], dataList[3]
    Sql = splitSql(yearList, monthList, dayList)
    Result = athenaQuery(Sql, "lazada_rtb_v3")
    csv_string = Result.get("data")
    lc = pd.DataFrame(pd.read_csv(StringIO(csv_string)))
    dayData = []
    hourData = []
    abnormal_list = []
    for i in range(2):
        bidcount = lc.loc[(lc["bid_day"] == dayList[i])].bidcount.sum()
        hourBidcount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i])].bidcount.sum()
        impCount = lc.loc[(lc["bid_day"] == dayList[i])].impCount.sum()
        hourImpCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i])].impCount.sum()
        clickCount = lc.loc[(lc["bid_day"] == dayList[i])].clickCount.sum()
        hourClickCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i])].clickCount.sum()
        postbackCount = lc.loc[(lc["bid_day"] == dayList[i])].postbackCount.sum()
        hourPostbackCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i])].postbackCount.sum()
        cost = lc.loc[(lc["bid_day"] == dayList[i])].cost.sum()
        hourCost = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i])].cost.sum()
        dayData.append({
            "bidcount": bidcount,
            "impCount": impCount,
            "clickCount": clickCount,
            "postbackCount": postbackCount,
            "cost": cost
        })
        hourData.append({
            "bidcount": hourBidcount,
            "impCount": hourImpCount,
            "clickCount": hourClickCount,
            "postbackCount": hourPostbackCount,
            "cost": hourCost
        })

    adx_list = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[0]) | (lc["bid_hour"] == hourList[1])].adx_id.unique()
    for adx_id in adx_list:
        adxData = []
        for i in range(2):
            adxBidcount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["adx_id"] == adx_id)].bidcount.sum()
            adxImpCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["adx_id"] == adx_id)].impCount.sum()
            adxClickCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["adx_id"] == adx_id)].clickCount.sum()
            adxPostbackCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["adx_id"] == adx_id)].postbackCount.sum()
            adxCost = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["adx_id"] == adx_id)].cost.sum()
            adxData.append({
                "bidcount": adxBidcount,
                "impCount": adxImpCount,
                "clickCount": adxClickCount,
                "postbackCount": adxPostbackCount,
                "cost": adxCost
            })
        for k, v in adxData[0].items():
            flag, diff = judge(float(adxData[0].get(k)), float(adxData[1].get(k)))
            if not flag:
                abnormal_list.append(f'adx-{adx_id}:{hourList[0]}-{hourList[1]}时间段-的{k}值差为{diff * 100}%')
    coutrys = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[0]) | (
                lc["bid_hour"] == hourList[1])].bid_country.unique()
    for coutry in coutrys:
        countryData = []
        for i in range(2):
            coutryBidcount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["bid_country"] == coutry)].bidcount.sum()
            coutryImpCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["bid_country"] == coutry)].impCount.sum()
            coutryClickCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["bid_country"] == coutry)].clickCount.sum()
            coutryPostbackCount = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["bid_country"] == coutry)].postbackCount.sum()
            coutryCost = lc.loc[(lc["bid_day"] == dayList[2]) & (lc["bid_hour"] == hourList[i]) & (lc["bid_country"] == coutry)].cost.sum()
            countryData.append({
                "bidcount": coutryBidcount,
                "impCount": coutryImpCount,
                "clickCount": coutryClickCount,
                "postbackCount": coutryPostbackCount,
                "cost": coutryCost
            })
        for k, v in countryData[0].items():
            flag, diff = judge(float(countryData[0].get(k)), float(countryData[1].get(k)))
            if not flag:
                abnormal_list.append(f'coutry-{coutry}:{hourList[0]}-{hourList[1]}时间段-的{k}值差为{diff * 100}%')

    for k, v in dayData[0].items():
        flag, diff = judge(float(dayData[0].get(k)), float(dayData[1].get(k)))
        if not flag:
            abnormal_list.append(f'day:{dayList[0]}-{dayList[1]}时间段-的{k}值差为{diff * 100}%')
    for k, v in hourData[0].items():
        flag, diff = judge(float(hourData[0].get(k)), float(hourData[1].get(k)))
        if not flag:
            abnormal_list.append(f'hour:{hourList[0]}-{hourList[1]}时间段-的{k}值差为{diff * 100}%')

    return abnormal_list

def send_notification(content):
    url = f"https://api.day.app/uq26MqRJ5T3TWAdAXDqsEm/{content}"
    requests.get(url)


if __name__ == "__main__":
    abnormal_list = dataContrast()
    if len(abnormal_list) > 0:
        content = ""
        for abnormal in abnormal_list:
            content+= f"{abnormal}-"
        send_notification(content)



