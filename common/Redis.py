'''
@Descripttion: 
@version: 
@Author: WGQ
@Date: 2020-02-28 16:01:47
LastEditors: WGQ
LastEditTime: 2021-11-14 22:18:51
'''
import redis

from common.Config import app_config

def getRedis():
    rdp = redis.ConnectionPool(host=app_config.REDIS_HOST, port=app_config.REDIS_PORT,
                            max_connections=100, password=app_config.REDIS_PASSWORD)
    cache = redis.StrictRedis(connection_pool=rdp)
    return cache
