'''
@Descripttion: 
@version: 
@Author: WGQ
@Date: 2020-06-23 17:52:54
LastEditors: WGQ
LastEditTime: 2021-11-11 16:22:52
'''
import os
# import sys
# sys.path.append("..")
from common.Config import app_configs

if not os.getenv("RUN_ENV"):
    os.environ["RUN_ENV"] = "dev"

print("Current ENV:"+os.getenv("RUN_ENV"))
appConfig = app_configs[os.getenv("RUN_ENV")]

dbs = appConfig.DATABASES
for db in dbs:
    mysqlDbName = db.get("MYSQL_NAME")
    mysqlUser = db.get("MYSQL_USER")
    mysqlHost = db.get("MYSQL_HOST")
    mysqlPwd = db.get("MYSQL_PASSWORD")
    mysqlModelName = db.get("MODEL_NAME")
    os.system("rm ./model/{}.py".format(mysqlModelName))
    print("python3 ./model/pwiz.py -e mysql -u {} -H {} --password {} {} > ./model/{}.py".format(mysqlUser,mysqlHost,mysqlPwd,mysqlDbName,mysqlModelName))
    os.system("python ./model/pwiz.py -e mysql -u {} -H {} --password {} {} > ./model/{}.py".format(mysqlUser,mysqlHost,mysqlPwd,mysqlDbName,mysqlModelName))