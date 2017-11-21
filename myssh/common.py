#coding:utf-8
import data
import time

def hideip_fun(ip):
    if data.hideip:
        temp_ip = ip.split('.')
        return temp_ip[0]+'.*.*.'+temp_ip[1]
    else:
        return ip


def strToTimestamp(dt):
    #转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    #转换成时间戳
    timestamp = time.mktime(timeArray)
    return timestamp
