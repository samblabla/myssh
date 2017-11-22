#coding:utf-8

import data
import ssh
import sftp
import common
import time


def threads_connect(name,i):
    ssh.create_conn(i)
    sftp.create_conn(i)
    print '\33[34m%d:\33[31m连接成功：%s(%s) \33[0m' %(i,data.servers[i]['name'],common.hideip_fun(data.servers[i]['host']))

def threads_handle(threads):
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()


def scan_document(name,server_num):
    data.client_file[server_num] = ssh.show_remote_file(
        server_num,
        data.paths[ server_num ] )


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
                if data.scp_isusing.has_key(i) and data.scp_isusing[i] == True :
                    continue
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
