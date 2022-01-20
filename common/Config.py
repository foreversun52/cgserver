'''
@Descripttion:
@version:
@Author: WGQ
@Date: 2020-05-26 15:07:25
LastEditors: WGQ
LastEditTime: 2021-11-15 12:09:28
'''
import os
# app配置文件
class Config(object):
    JWT_SECRET = "CCGG6688"
    ALIYUNOSS_ENDPOINT = "oss-cn-hangzhou.aliyuncs.com"
    WECHAT_APPID = "wx7cec9e4982f88258"  # 微信AppID
    WECHAT_APPSECRET = "a0e9130d14ca7615085190e6ff2393c7"
    WECHAT_TOKEN = "forever92"
    WECHAT_EncodingAESKey = "D2MZu5o9dp4TaKL8sVdf3BjxyCTJNGzXOuPwWI8YFSr"

class DevConfig(Config):
    ENV_NAME = "DEV"
    # 开发环境配置
    DEBUG = True
    PORT = 12233

    # 非关系型数据库的配置
    REDIS_HOST = "42.192.51.96"
    REDIS_PORT = 6379
    REDIS_PASSWORD = ""

    DATABASES = [
        {
            "MYSQL_HOST" : "42.192.51.96",
            "MYSQL_NAME" : "db_cash_gift",
            "MYSQL_USER" : "root",
            "MYSQL_PASSWORD" : "root",
            "MYSQL_PORT" : 3306,
            "MODEL_NAME" : "CModel"
        }
    ]

    ALIYUNOSS_ENDPOINT = ""


class LocalConfig(Config):
    ENV_NAME = "LOCAL"
    # 开发环境配置
    DEBUG = True
    PORT = 16688

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_PASSWORD = ""

    DATABASES = [
        {
            "MYSQL_HOST" : "127.0.0.1",
            "MYSQL_NAME" : "app_rtb",
            "MYSQL_USER" : "root",
            "MYSQL_PASSWORD" : "123456",
            "MYSQL_PORT" : 3369,
            "MODEL_NAME" : "RModel"
        }
    ]


class ReleaseConfig(Config):
    ENV_NAME = "Release"
    # 发布环境
    DEBUG = False
    PORT = 34567
    REDIS_HOST = "caibortbredis.y7xo7q.ng.0001.apse1.cache.amazonaws.com"
    REDIS_PORT = 6379
    REDIS_PASSWORD = ""

    DATABASES = [
        {
            "MYSQL_HOST" : "127.0.0.1",
            "MYSQL_NAME" : "app_rtb",
            "MYSQL_USER" : "app_rtb",
            "MYSQL_PASSWORD" : "bCukw-!2jOv4k]c@",
            "MYSQL_PORT" : 3369,
            "MODEL_NAME" : "RModel"
        }
    ]

app_configs = {
    "dev":DevConfig,
    "local":LocalConfig,
    "release":ReleaseConfig
}

if not os.getenv("RUN_ENV"):
    os.environ["RUN_ENV"] = "dev"

app_config = app_configs[os.environ["RUN_ENV"]]