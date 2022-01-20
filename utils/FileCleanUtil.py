# 定时清除 一周前的文件
import os, time, shutil

def check_file(file):
    f_time = os.path.getmtime(file)
    now_time = time.time()
    out_time = int(now_time - f_time)
    seven_days = 7 * 24 * 60 * 60
    if out_time > seven_days:
        if os.path.isdir(file):
            shutil.rmtree(file, ignore_errors=True)
        else:
            os.remove(file)


def cleanFile():
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_path, 'static')
    file_list = os.listdir(file_path)
    for file_path_name in file_list:
        _file_path_name = os.path.join(file_path, file_path_name)
        if file_path_name == 'chunk' or file_path_name == 'down_wav':
            for file_name in os.listdir(_file_path_name):
                _file_name = os.path.join(_file_path_name, file_name)
                check_file(_file_name)
        elif os.path.isdir(_file_path_name) and len(file_path_name) == 32:
            _file_path = os.path.join(file_path, file_path_name)
            check_file(_file_path)