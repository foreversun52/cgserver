'''
Descripttion:
version:
Author: WGQ
Date: 2020-05-26 15:07:25
LastEditors: WGQ
LastEditTime: 2020-12-25 10:28:56
'''
# -*- coding:utf-8 -*-
import re, os, requests


def getClientIp(request,format = "ip"):
    """ 获取客户端IP """
    realIp = "0.0.0.0"
    try:
        if request.headers.get('x-forwarded-for') is not None:
            xForwardFor = request.headers.get('x-forwarded-for')
            realIp = str.strip(str.split(xForwardFor)[0])
        elif request.headers.get('x-real-ip') is not None:
            xRealIp = request.headers.get('x-real-ip')
            realIp = str.strip(str.split(xRealIp)[0])
        else:
            realIp = str(request.remote_addr)
    except:
        realIp = "0.0.0.0"
    realIp = realIp.replace(",", "")
    if format == "long":
        realIp = ip2long(realIp)
    return realIp


def ip2long(ip):
    """ ip to long """
    try:
        ip_list = ip.split('.')
        result = 0
        for i in range(4):  # 0,1,2,3
            result = result + int(ip_list[i]) * 256 ** (3 - i)
        return result
    except:
        return 0


def long2ip(long):
    """ convert int to ip """
    floor_list = []
    yushu = long
    for i in reversed(range(4)):  # 3,2,1,0
        res = divmod(yushu, 256 ** i)
        floor_list.append(str(res[0]))
        yushu = res[1]
    return '.'.join(floor_list)


def validMobilephone(mobilephone):
    """ 是否是合法的手机验证码 """
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    res = re.search(phone_pat, mobilephone)
    if res:
        return True
    else:
        return False


def ServerIp():
    """服务器ip"""
    server_Ip = 'http://127.0.0.1:16688'
    return server_Ip


def AsrIp():
    """ASR离线识别服务器ip"""
    Asr_Ip = 'http://127.0.0.1:9988'
    return Asr_Ip


# def show_files(path, all_files, attachment_file_path):
#     """获取文件夹所有文件"""
#     file_list = os.listdir(path)
#
#     for file in file_list:
#         if file == '__MACOSX' or file == '.DS_Store':
#             continue
#         cur_path = os.path.join(path, file)
#         if cur_path == attachment_file_path:
#             continue
#         if os.path.isdir(cur_path):
#             show_files(cur_path, all_files, attachment_file_path)
#         else:
#             _type = magic.from_buffer(open(cur_path, "rb").read(2048), mime=True)
#             new_type = _type.split('/')[0]
#             if new_type == 'audio':
#                 file_type = '音频'
#             elif new_type == 'text':
#                 file_type = '文本'
#             elif new_type == 'video':
#                 file_type = '视频'
#             elif new_type == 'image':
#                 file_type = '图片'
#             else:
#                 file_type = '未知类型'
#             fileInfo = {}
#             server_ip = ServerIp()
#             print(cur_path)
#             url = cur_path.split("static")[-1]
#             if '/' in url:
#                 url = url.split('/')
#             elif '\\' in url:
#                 url = url.split('\\')
#             fileUrl = f'{server_ip}/static'
#             for _url in url:
#                 if _url:
#                     fileUrl += f'/{_url}'
#             fileInfo['fileUrl'] = fileUrl
#             fileInfo['fileName'] = file
#
#             fileInfo['fileType'] = file_type
#             all_files.append(fileInfo)
#     return all_files


def get_text(file_path):
    """将处理后的wav文件传入asr进行文字识别"""
    res = ""
    asr_ip = AsrIp()
    try:
        new_url = f'{asr_ip}/asr.php?file={file_path}&'
        r = requests.get(url=new_url)
        r.encoding=r.apparent_encoding
        res = r.text
    except:
        pass
    return res