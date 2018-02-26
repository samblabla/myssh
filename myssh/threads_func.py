#coding:utf-8

import data
import ssh
import sftp
import common
import time
import threading

import pexpect  

def ssh_verify(name, i):

    server_info = data.servers[i]
    if('port' in server_info):
        port = server_info['port']
    else:
        port = 22
    cmd = 'cd ;ls;'
    ssh = pexpect.spawn('ssh %s@%s  -p %s  "%s"' %(
        server_info['user'],
        server_info['host'],
        port,
        cmd))
    msg = '\33[34m%d:\33[33m%s@%s(%s):\33[0m ' %(
        i,
        server_info['user'],
        server_info['name'],
        common.hideipFun(server_info['host'])
        )
    
    try:
        status = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=20)
        if status == 0 :
            ssh.sendline(server_info['password'])
            ssh.sendline(cmd)
            print(msg+' \033[32mSuccess\033[0m')
        elif status == 1:
            ssh.sendline('yes\n')
            ssh.expect('password: ')
            ssh.sendline(server_info['password'])
            ssh.sendline(cmd)
            print(msg+' \033[32mAdd public key successfully\033[0m')
        ssh.close()
        return
    except pexpect.EOF:
        print(msg+' \033[31mEOF\033[0m')
        ssh.close()
    except pexpect.TIMEOUT:
        print(msg+' \033[31mTimeout\033[0m')
        ssh.close()
    

def threads_connect(name,i):
    ssh.create_conn(i)
    sftp.create_conn(i)
    print('\33[34m%d:\33[31m%s成功：%s(%s) \33[0m' %(i,name,data.servers[i]['name'],common.hideipFun(data.servers[i]['host'])))

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
        except (ExceptionType) as e:
            print('\n')

            reconnect_threads = []
            for server_num in ssh_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                reconnect_threads.append( threading.Thread(target=threads_connect,args=('重连',server_num)) )
            threads_handle(reconnect_threads)

            for i in ssh_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m ' %(
                    i,
                    data.servers[i]['user'],
                    data.servers[i]['name'],
                    common.hideipFun(data.servers[i]['host'])
                    ,
                    data.paths[i] ))
        time.sleep(30)

def heartbeat_scp(scp_conns,close_i):
    while 1:
        if data.heartbeat_paramiko_close[close_i]:
            break
        try:
            for i in scp_conns:
                if i in data.scp_isusing and data.scp_isusing[i] == True :
                    continue
                scp_conns[i].listdir_attr('/')
        except (ExceptionType) as e:
            print('\n')
            reconnect_threads = []
            for server_num in scp_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                reconnect_threads.append( threading.Thread(target=threads_connect,args=('重连',server_num)) )
            threads_handle(reconnect_threads)
            for i in scp_conns:
                if data.heartbeat_paramiko_close[close_i]:
                    break
                print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m ' %(
                    i,
                    data.servers[i]['user'],
                    data.servers[i]['name'],
                    common.hideipFun(data.servers[i]['host'])
                    ,
                    data.paths[i] ))
        time.sleep(30)
