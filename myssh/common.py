#coding:utf-8
import data

def hideip_fun(ip):
    if data.hideip:
        temp_ip = ip.split('.')
        return temp_ip[0]+'.*.*.'+temp_ip[1]
    else:
        return ip