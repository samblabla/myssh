#coding:utf-8

import data
import common
import time

''' def threads_connect():
    print '\33[34m%d:\33[31m正在连接：%s(%s) \33[0m' %(server_num,server_info['name'],common.hideip_fun(server_info['host']))
    create_ssh_conn(server_num)
    create_scp_conn(server_num)
 '''



#ssh心跳定时执行是否关闭
def heartbeat_ssh(ssh_conns,close_i):
    while 1:
        if data.heartbeat_paramiko_close[close_i]:
            break
        try:
            for i in ssh_conns:
                ssh_conns[i].exec_command('pwd')
        except Exception,e:
            print '\n'
            for i in ssh_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                print '重连ssh ',i
                ssh.create_conn(i)
            for i in ssh_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m ' %(
                    i,
                    data.servers[i]['user'],
                    data.servers[i]['name'],
                    common.hideip_fun(data.servers[i]['host'])
                    ,
                    data.paths[i] ))
        time.sleep(30)

def heartbeat_scp(scp_conns,close_i):
    while 1:
        if data.heartbeat_paramiko_close[close_i]:
            break
        try:
            for i in scp_conns:
                scp_conns[i].listdir_attr('/')
        except Exception,e:
            print '\n'
            for i in scp_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                print '重连scp ',i
                sftp.create_conn(i)
            for i in scp_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m ' %(
                    i,
                    data.servers[i]['user'],
                    data.servers[i]['name'],
                    common.hideip_fun(data.servers[i]['host'])
                    ,
                    data.paths[i] ))
        time.sleep(30)
