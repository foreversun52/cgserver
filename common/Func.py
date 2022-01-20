import json,random,string,hashlib,math,time
from .Encrypt import Encrypt
import decimal
from html.parser import HTMLParser
from fastapi.responses import PlainTextResponse, JSONResponse
def makeResult(data=None, message='success', status=100000200, outer_id=0):
    encryptUtil = Encrypt()
    timestamp = int(time.time())
    rt = {"data": encryptUtil.apiDataEncrypt(json.dumps(data)), "message": message, "status": status, "server_time":timestamp}
    return rt


def jsonResult(data=None, message='success', status=100000200):
    timestamp = int(time.time())
    rt = {"data": data, "message": message, "status": status, "server_time": timestamp}
    # print(rt)
    return rt


def jsonPResult(data=None, callbackFunction = "", message='success', status=100000200):
    timestamp = int(time.time())
    rt = {"data": data, "message": message, "status": status, "server_time": timestamp}
    return PlainTextResponse(content = "{}({})".format(callbackFunction,json.dumps(rt)))


def strip_tags(html, save=None):
    result = []
    start = []
    data = []

    def starttag(tag, attrs):
        if tag not in save:
            return
        start.append(tag)
        if attrs:
            j = 0
            for attr in attrs:
                attrs[j] = attr[0] + '="' + attr[1] + '"'
                j += 1
            attrs = ' ' + (' '.join(attrs))
        else:
            attrs = ''
        result.append('<' + tag + attrs + '>')

    def endtag(tag):
        if start and tag == start[len(start) - 1]:
            result.append('</' + tag + '>')

    parser = HTMLParser()
    parser.handle_data = result.append
    if save:
        parser.handle_starttag = starttag
        parser.handle_endtag = endtag
    parser.feed(html)
    parser.close()

    for i in range(0, len(result)):
        tmp = result[i].rstrip('\n')
        tmp = tmp.lstrip('\n')
        if tmp:
            data.append(tmp)

    return ''.join(data)

def randomStr(length):
    randStr = str(''.join(random.choices(string.ascii_uppercase + string.digits, k=length)))
    return randStr

def md5(str):
    m2 = hashlib.md5()
    m2.update(str.encode('utf-8'))
    token = m2.hexdigest()
    return token

def outputPageInfo(page,pageSize,totalCount):
    return {"page":page,"page_size":pageSize,"total_count":totalCount,"total_page":math.ceil( totalCount * 1.0/pageSize )}

