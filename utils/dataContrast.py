# -*- coding: UTF-8 -*-
'''
@Project :dspserver
@File    :dataContrast.py
@IDE     :PyCharm
@Author  :Forever
@Date    :2021/12/27 16:54
'''
import time, boto3, requests
from io import StringIO
from datetime import datetime
import pandas as pd
import hmac,hashlib,base64,urllib.parse


def athenaQuery(sql, database):
    S3_KEY = "AKIA4P3WFQJIJNSYQMT6"
    S3_SECRET = "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"
    S3_BUCKET = "lzdlog"
    # return_data = {'status': False, 'data': '', 'msg': 'success'}
    # s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'), region_name='ap-southeast-1', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    # key = "queryresult/" + "71bbe207-77b6-400e-a825-9cefb99c16f1.csv"
    # obj = s3.get_object(Bucket=S3_BUCKET, Key=key)['Body'].read().decode("utf-8")
    # return_data['status'] = True
    # return_data['data'] = obj
    # return return_data
    s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'), region_name='ap-southeast-1', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    athena = boto3.client('athena', region_name='ap-southeast-1', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    outputLocation = "s3://lzdlog/queryresult/"
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': outputLocation
        }
    )
    fileName = response['QueryExecutionId'] + '.csv'
    key = "queryresult/" + fileName
    returnData = {'status': False, 'data': '', 'msg': 'success'}
    for i in range(15):
        try:
            time.sleep(1)
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)['Body'].read().decode("utf-8")
            returnData['status'] = True
            returnData['data'] = obj
            return returnData
        except Exception as e:
            returnData['msg'] = e
            # return return_data
    else:
        returnData['msg'] = 'no data'
        return returnData


def judge(a, b):
    # a 是前前一个时间段的数据，b 是前一个时间段的数据  a 比 b大 代表 降低，b 比a大代表增长 默认 b比a大，如果a比b大 值交换 状态改为降低
    status = "增长"
    if a > b:
        status = "降低"
    if a == 0:
        status = "异常"
        return (False, status, 0)
    if a > b:
        difference = round((a-b)/a, 2)
    else:
        difference = round((b-a)/a, 2)
    if difference > 0.3:
        return (False,status, difference)
    return (True,status, difference)


def makeSQL(year, month, day):
    Sql = f"""SELECT bid_month,
               bid_day,
               bid_hour,
               bid_country,
               adx_id,
               sum(bidCount) AS bidCount,
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
                  count(b.bid_id) AS bidCount,
                  sub_type,
                  bid_request.app.bundle AS appbundle,
                  b.imp_width,
                  b.imp_height,
                  count(i.bid_id) AS impCount,
                  count(c.bid_id) AS clickCount,
                  count(pb.p_deviceid) AS postbackCount,
                  bid_price
           FROM lazada_rtb_v3.bid_log AS b
           LEFT JOIN
             (SELECT DISTINCT bid_id
              FROM lazada_rtb_v3.impression_log) AS i ON b.bid_id = i.bid_id
           LEFT JOIN
             (SELECT DISTINCT bid_id,
                              device_id
              FROM lazada_rtb_v3.click_log) AS c ON c.bid_id = b.bid_id
           LEFT JOIN
             (SELECT DISTINCT device_id AS p_deviceid,
                              bid_id
              FROM lazada_rtb_v3.post_back_log
              WHERE device_id <> ''
                AND event IN ('first_launch', 'activation')
                AND ((post_back_year = {year}
                AND post_back_month = {month}
                AND post_back_day = {day})) ) AS pb ON pb.bid_id = b.bid_id
           WHERE bid_year= {year}
             AND bid_month = {month}
             AND bid_day  = {day}
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


def getCsvDataFrame():
    dateList = getDate()
    yearList, monthList, dayList, hourList = dateList[0], dateList[1], dateList[2], dateList[3]
    yesterdaySql = makeSQL(yearList[1], monthList[1], dayList[1])
    yesterdayResult = athenaQuery(yesterdaySql, "lazada_rtb_v3")
    yesterdayCsvString = yesterdayResult.get("data")
    yesterdayCsvObj = pd.read_csv(StringIO(yesterdayCsvString))
    todaySql = makeSQL(yearList[2], monthList[2], dayList[2])
    todayResult = athenaQuery(todaySql, "lazada_rtb_v3")
    todayCsvString = todayResult.get("data")
    todayCsvObj= pd.read_csv(StringIO(todayCsvString))
    if hourList[1] == 1:
        beforeYesterdaySql = makeSQL(yearList[0], monthList[0], dayList[0])
        beforeYesterdayResult = athenaQuery(beforeYesterdaySql, "lazada_rtb_v3")
        beforeYesterdayCsvString = beforeYesterdayResult.get("data")
        beforeYesterdayCsvObj= pd.read_csv(StringIO(beforeYesterdayCsvString))
        csvList = [yesterdayCsvObj, todayCsvObj, beforeYesterdayCsvObj]
    else:
        csvList = [yesterdayCsvObj, todayCsvObj]
    mergeCsv = pd.concat(csvList)
    dataFrame = pd.DataFrame(mergeCsv)
    return dataFrame


def dayDataContrast(dataFrame, dateList):
    yearList, monthList, dayList, hourList = dateList[0], dateList[1], dateList[2], dateList[3]
    # hourList[1] 是上个小时 hourList[0]是上上个小时
    dayAbnormalList = []
    if hourList[1] == 1:
        dayData = []
        for i in range(2):
            bidCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[i])].bidCount.sum()
            impCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[i])].impCount.sum()
            clickCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[i])].clickCount.sum()
            postbackCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[i])].postbackCount.sum()
            cost = dataFrame.loc[(dataFrame["bid_day"] == dayList[i])].cost.sum()
            dayData.append({
                "BID": bidCount,
                "IMP": impCount,
                "CLK": clickCount,
                "PB": postbackCount,
                "Cost": round(cost, 2)
            })
        dayReport = "全局:昨日与前日的对比:\n"
        for k, v in dayData[0].items():
            flag, status, diff = judge(float(dayData[0].get(k)), float(dayData[1].get(k)))
            dayReport += f'{k}:昨日{dayData[1].get(k)}，前日:{dayData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
        dayReport += "-----------------------------------\n"
        dayAbnormalList.append(dayReport)
        dayCountryReport = "Country:\n"
        dayBidCoutries = dataFrame.loc[
            (dataFrame["bid_day"] == dayList[0]) | (dataFrame["bid_day"] == dayList[1])].bid_country.unique()
        for dayBidCoutry in dayBidCoutries:
            report = f"{dayBidCoutry}:\n"
            dayCountryData = []
            for i in range(2):
                coutryBidcount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_country"] == dayBidCoutry)].bidCount.sum()
                coutryImpCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_country"] == dayBidCoutry)].impCount.sum()
                coutryClickCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_country"] == dayBidCoutry)].clickCount.sum()
                coutryPostbackCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[i]) & (
                            dataFrame["bid_country"] == dayBidCoutry)].postbackCount.sum()
                coutryCost = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_country"] == dayBidCoutry)].cost.sum()
                dayCountryData.append({
                    "BID": coutryBidcount,
                    "IMP": coutryImpCount,
                    "CLK": coutryClickCount,
                    "PB": coutryPostbackCount,
                    "Cost": round(coutryCost, 2)
                })
            for k, v in dayCountryData[0].items():
                flag, status, diff = judge(float(dayCountryData[0].get(k)), float(dayCountryData[1].get(k)))
                report += f'{k}:昨日{dayCountryData[1].get(k)}，前日:{dayCountryData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
            dayCountryReport += report
        dayCountryReport += "-----------------------------------\n"
        dayAbnormalList.append(dayCountryReport)
        dayAdxReport = "Adx:\n"
        dayAdxIds = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[0]) | (
                dataFrame["bid_hour"] == hourList[1])].adx_id.unique()
        for dayAdxId in dayAdxIds:
            report = f"{dayAdxId}:\n"
            dayAdxData = []
            for i in range(2):
                adxBidcount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["adx_id"] == dayAdxId)].bidCount.sum()
                adxImpCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["adx_id"] == dayAdxId)].impCount.sum()
                adxClickCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["adx_id"] == dayAdxId)].clickCount.sum()
                adxPostbackCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["adx_id"] == dayAdxId)].postbackCount.sum()
                adxCost = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[i]) & (dataFrame["adx_id"] == dayAdxId)].cost.sum()
                dayAdxData.append({
                    "BID": adxBidcount,
                    "IMP": adxImpCount,
                    "CLK": adxClickCount,
                    "PB": adxPostbackCount,
                    "Cost": round(adxCost, 2)
                })
            for k, v in dayAdxData[0].items():
                flag, status, diff = judge(float(dayAdxData[0].get(k)), float(dayAdxData[1].get(k)))
                report += f'{k}:昨日{dayAdxData[1].get(k)}，前日:{dayAdxData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'

            dayAdxReport += report
        dayAdxReport += "-----------------------------------\n"
        dayAbnormalList.append(dayAdxReport)
    return dayAbnormalList


def hourDataContrast(dataFrame, dateList):
    dateList = getDate()
    yearList, monthList, dayList, hourList = dateList[0], dateList[1], dateList[2], dateList[3]
    hourAllData = []
    hourAbnormalList = []
    isAdd = False
    hourAllReport = "小时级指标对比\n"
    report = "小时级全局对比昨日\n"
    # 昨日和今天当前UTC小时 对比
    for i in range(1,3):
        hourBidcount = dataFrame.loc[
            (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1])].bidCount.sum()
        hourImpCount = dataFrame.loc[
            (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1])].impCount.sum()
        hourClickCount = dataFrame.loc[
            (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1])].clickCount.sum()
        hourPostbackCount = dataFrame.loc[
            (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1])].postbackCount.sum()
        hourCost = dataFrame.loc[
            (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1])].cost.sum()
        hourAllData.append({
            "BID": hourBidcount,
            "IMP": hourImpCount,
            "CLK": hourClickCount,
            "PB": hourPostbackCount,
            "Cost": round(hourCost, 2)
        })

    for k, v in hourAllData[0].items():
        flag, status, diff = judge(float(hourAllData[0].get(k)), float(hourAllData[1].get(k)))
        if not flag:
            report += f'{k}-ALL-ALL:UTC-{hourList[1]}:{hourAllData[1].get(k)}，昨日UTC-{hourList[1]}:{hourAllData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
            isAdd = True
    if isAdd:
        hourAllReport += report
        hourAllReport += "-----------------------------------\n"
        hourAbnormalList.append(hourAllReport)
        isAdd = False

    hourRefineCountryReport = "小时级指标Country对比昨日\n"
    # 细化指标Country对比昨日
    bidCoutries = dataFrame.loc[(dataFrame["bid_day"] == dayList[1]) | (dataFrame["bid_day"] == dayList[2]) & (
            dataFrame["bid_hour"] == hourList[1])].bid_country.unique()
    for bidCoutry in bidCoutries:
        report = f"{bidCoutry}:\n"
        addReport = False
        hourRefineCountryData = []
        for i in range(1, 3):
            coutryBidcount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["bid_country"] == bidCoutry)].bidCount.sum()
            coutryImpCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["bid_country"] == bidCoutry)].impCount.sum()
            coutryClickCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["bid_country"] == bidCoutry)].clickCount.sum()
            coutryPostbackCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["bid_country"] == bidCoutry)].postbackCount.sum()
            coutryCost = dataFrame.loc[(dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                    dataFrame["bid_country"] == bidCoutry)].cost.sum()
            hourRefineCountryData.append({
                "BID": coutryBidcount,
                "IMP": coutryImpCount,
                "CLK": coutryClickCount,
                "PB": coutryPostbackCount,
                "Cost": round(coutryCost, 2)
            })
        for k, v in hourRefineCountryData[0].items():
            flag, status, diff = judge(float(hourRefineCountryData[0].get(k)), float(hourRefineCountryData[1].get(k)))
            if not flag:
                report += f'{k}-{bidCoutry}:UTC-{hourList[1]}:{hourRefineCountryData[1].get(k)}，昨日UTC-{hourList[1]}:{hourRefineCountryData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
                isAdd = True
                addReport = True
        if addReport:
            hourRefineCountryReport += report

    if isAdd:
        hourRefineCountryReport += "-----------------------------------\n"
        hourAbnormalList.append(hourRefineCountryReport)
        isAdd = False

    hourRefineAdxReport = "小时级指标Adx对比昨日\n"
    adxIds = dataFrame.loc[(dataFrame["bid_day"] == dayList[1])| (dataFrame["bid_day"] == dayList[2]) &  (dataFrame["bid_hour"] == hourList[1])].adx_id.unique()
    for adxId in adxIds:
        adxData = []
        report = f"{adxId}:\n"
        addReport = False
        for i in range(1, 3):
            adxBidcount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (dataFrame["adx_id"] == adxId)].bidCount.sum()
            adxImpCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["adx_id"] == adxId)].impCount.sum()
            adxClickCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["adx_id"] == adxId)].clickCount.sum()
            adxPostbackCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                        dataFrame["adx_id"] == adxId)].postbackCount.sum()
            adxCost = dataFrame.loc[(dataFrame["bid_day"] == dayList[i]) & (dataFrame["bid_hour"] == hourList[1]) & (
                    dataFrame["adx_id"] == adxId)].cost.sum()
            adxData.append({
                "BID": adxBidcount,
                "IMP": adxImpCount,
                "CLK": adxClickCount,
                "PB": adxPostbackCount,
                "Cost": round(adxCost, 2)
            })
        for k, v in adxData[0].items():
            flag, status, diff = judge(float(adxData[0].get(k)), float(adxData[1].get(k)))
            if not flag:
                report += f'{k}-{adxId}:UTC-{hourList[1]}:{adxData[1].get(k)}，昨日UTC-{hourList[1]}:{adxData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
                isAdd = True
                addReport = True
        if addReport:
            hourRefineAdxReport += report
    if isAdd:
        hourRefineAdxReport += "-----------------------------------\n"
        hourAbnormalList.append(hourRefineAdxReport)
        isAdd = False

    if hourList[1] >=2 and hourList[1] <= 16:
        hourTodayReport = "小时级全局对比前小时\n"
        hourTodayData = []
        # 今天上个小时与前一个小时全局对比
        for i in range(2):
            hourBidcount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i])].bidCount.sum()
            hourImpCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i])].impCount.sum()
            hourClickCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i])].clickCount.sum()
            hourPostbackCount = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i])].postbackCount.sum()
            hourCost = dataFrame.loc[
                (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i])].cost.sum()
            hourTodayData.append({
                "BID": hourBidcount,
                "IMP": hourImpCount,
                "CLK": hourClickCount,
                "PB": hourPostbackCount,
                "Cost": round(hourCost, 2)
            })

        for k, v in hourTodayData[0].items():
            flag, status, diff = judge(float(hourTodayData[0].get(k)), float(hourTodayData[1].get(k)))
            if not flag:
                hourTodayReport += f'{k}-ALL:UTC-{hourList[1]}:{hourTodayData[1].get(k)}，UTC-{hourList[0]}:{hourTodayData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
                isAdd = True
        if isAdd:
            hourTodayReport += "-----------------------------------\n"
            hourAbnormalList.append(hourTodayReport)
            isAdd = False

        hourRefineCountryTodayReport = "细化指标Country上一小时对比前小时\n"
        # 细化指标Country上一个小时对比前一个小时
        bidCoutries = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[0]) | (dataFrame["bid_hour"] == hourList[1])].bid_country.unique()
        for bidCoutry in bidCoutries:
            report = f"{bidCoutry}:\n"
            addReport = False
            countryData = []
            for i in range(2):
                coutryBidcount = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (dataFrame["bid_country"] == bidCoutry)].bidCount.sum()
                coutryImpCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (dataFrame["bid_country"] == bidCoutry)].impCount.sum()
                coutryClickCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (dataFrame["bid_country"] == bidCoutry)].clickCount.sum()
                coutryPostbackCount = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (dataFrame["bid_country"] == bidCoutry)].postbackCount.sum()
                coutryCost = dataFrame.loc[(dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (dataFrame["bid_country"] == bidCoutry)].cost.sum()
                countryData.append({
                    "BID": coutryBidcount,
                    "IMP": coutryImpCount,
                    "CLK": coutryClickCount,
                    "PB": coutryPostbackCount,
                    "Cost": round(coutryCost, 2)
                })
            for k, v in countryData[0].items():
                flag,status, diff = judge(float(countryData[0].get(k)), float(countryData[1].get(k)))
                if not flag:
                    report += f'{k}-{bidCoutry}:UTC-{hourList[1]}:{countryData[1].get(k)}，UTC-{hourList[0]}:{countryData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
                    isAdd = True
                    addReport = True
            if addReport:
                hourRefineCountryTodayReport += report
        if isAdd:
            hourRefineCountryTodayReport += "-----------------------------------\n"
            hourAbnormalList.append(hourRefineCountryTodayReport)
            isAdd = False
        hourRefineAdxTodayReport = "细化指标Adx上一小时对比前小时\n"
        adxIds = dataFrame.loc[(dataFrame["bid_day"] == dayList[2])  & (dataFrame["bid_hour"] == hourList[0]) | (dataFrame["bid_hour"] == hourList[1])].adx_id.unique()
        for adxId in adxIds:
            adxData = []
            report = f"{adxId}:\n"
            addReport = False
            for i in range(2):
                adxBidcount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (
                                dataFrame["adx_id"] == adxId)].bidCount.sum()
                adxImpCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (
                            dataFrame["adx_id"] == adxId)].impCount.sum()
                adxClickCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (
                            dataFrame["adx_id"] == adxId)].clickCount.sum()
                adxPostbackCount = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (
                            dataFrame["adx_id"] == adxId)].postbackCount.sum()
                adxCost = dataFrame.loc[
                    (dataFrame["bid_day"] == dayList[2]) & (dataFrame["bid_hour"] == hourList[i]) & (
                            dataFrame["adx_id"] == adxId)].cost.sum()
                adxData.append({
                    "BID": adxBidcount,
                    "IMP": adxImpCount,
                    "CLK": adxClickCount,
                    "PB": adxPostbackCount,
                    "Cost": round(adxCost, 2)
                })
            for k, v in adxData[0].items():
                flag, status, diff = judge(float(adxData[0].get(k)), float(adxData[1].get(k)))
                if not flag:
                    report += f'{k}-{adxId}:UTC-{hourList[1]}:{adxData[1].get(k)}，UTC-{hourList[0]}:{adxData[0].get(k)},{status}了{round(diff * 100, 2)}%\n'
                    isAdd = True
                    addReport = True
            if addReport:
                hourRefineAdxTodayReport += report
        if isAdd:
            hourRefineAdxTodayReport += "-----------------------------------\n"
            hourAbnormalList.append(hourRefineAdxTodayReport)
    return hourAbnormalList


def send_notification(content):
    url = f"https://api.day.app/uq26MqRJ5T3TWAdAXDqsEm/{content}"
    requests.get(url)


def sendToDingTalk(message):
    timestamp = str(round(time.time() * 1000))
    sign = dingTalkSign(timestamp)
    url = f"https://oapi.dingtalk.com/robot/send?access_token=9a53f4cdcfeb274066cd0768d06b1fb09544e79c6b6cb20630091ed6bd11bf5e&timestamp={timestamp}&sign={sign}"
    rt = requests.post(url, json={"msgtype": "text", "text": {"content": message}})
    print(url)
    print(rt.text)


def dingTalkSign(timestamp):
    secret = 'SECded92fcb0e635d377edcec82dc3f426d9321fb4e9af305235ac9341469f8b0ad'
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


if __name__ == "__main__":
    _nowHour = datetime.utcfromtimestamp(int(time.time())).hour
    if (_nowHour >=18 and _nowHour <=23 ) or (_nowHour < 2):
        pass
    else:
        dateList = getDate()
        yearList, monthList, dayList, hourList = dateList[0], dateList[1], dateList[2], dateList[3]
        dataFrame = getCsvDataFrame()
        dayAbnormalList = dayDataContrast(dataFrame, dateList)
        hourAbnormalList = hourDataContrast(dataFrame, dateList)
        if len(dayAbnormalList) > 0:
            # 全日
            content = ""
            for abnormal in dayAbnormalList:
                content += abnormal
            sendToDingTalk(content)
        if len(hourAbnormalList) > 0:
            # 小时级
            content = ""
            for abnormal in hourAbnormalList:
                content += abnormal
            sendToDingTalk(content)