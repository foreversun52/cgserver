'''
@Descripttion: 
@version: 
@Author: WGQ
@Date: 2020-02-11 09:29:01
@LastEditors: WGQ
@LastEditTime: 2020-03-27 17:58:29
'''

import hashlib,base64
from Crypto.Cipher import AES

class Encrypt:
    def urlParamEncrypt(self,param):
        hash = hashlib.sha384('1d2e784297f606f4'.encode("utf-8")).hexdigest().upper()
        key  = hash [0:16]
        iv = hash[32:48]
        length = 16                    # 这里只是用于下面取余前面别以为是配置
        count = len(param.encode('utf-8'))
        obj = AES.new(str.encode(key), AES.MODE_CBC, str.encode(iv))
        if (count % length != 0):
            add = length - (count % length)
        else:
            add = 0             #  看看你们对接是满16的时候加上16还是0.这里注意
        message = param + ('\0' * add)    # 其它语言nopadding时，python还是需要‘\0’或'\x00'这里注意与其它语言对接注意
        ciphertext = obj.encrypt(str.encode(message))
        return str(base64.b64encode(ciphertext),encoding='utf8')

    def urlParamDecrypt(self,param):
        hash = hashlib.sha384('1d2e784297f606f4'.encode("utf-8")).hexdigest().upper()
        key  = hash [0:16]
        iv = hash[32:48]
        obj = AES.new(str.encode(key), AES.MODE_CBC, str.encode(iv))
        encryptedData = base64.b64decode(str.encode(param))
        encryptedStr = str(obj.decrypt(encryptedData),encoding = "utf8")
        return str(encryptedStr.rstrip())

    def apiDataEncrypt(self, param):
        hash = hashlib.sha384('98facef8dfc392ba'.encode("utf-8")).hexdigest().upper()
        key = hash[0:16]
        iv = hash[32:48]
        length = 16                    # 这里只是用于下面取余前面别以为是配置
        count = len(param.encode('utf-8'))
        obj = AES.new(str.encode(key), AES.MODE_CBC, str.encode(iv))
        if (count % length != 0):
            add = length - (count % length)
        else:
            add = 0             #  看看你们对接是满16的时候加上16还是0.这里注意
        message = param + ('\0' * add)    # 其它语言nopadding时，python还是需要‘\0’或'\x00'这里注意与其它语言对接注意
        ciphertext = obj.encrypt(str.encode(message))
        return str(base64.b64encode(ciphertext), encoding='utf8')

    def apiDataDecrypt(self, param):
        hash = hashlib.sha384('98facef8dfc392ba'.encode("utf-8")).hexdigest().upper()
        key = hash[0:16]
        iv = hash[32:48]
        obj = AES.new(str.encode(key), AES.MODE_CBC, str.encode(iv))
        encryptedData = base64.b64decode(param)
        encryptedStr = str(obj.decrypt(encryptedData),encoding="utf8")
        return str(encryptedStr.rstrip())
