#coding:utf-8

import os
from socket import socket
from sshtunnel import SSHTunnelForwarder
import data
import config
import threads_func
import springboard
import common

import pexpect  

sshpass = config.sshpass

def login(server_num,server_info):
    known_host = os.popen("ssh-keygen -F %s" %server_info['host'])
    if(known_host.read() == ''):
        if('springboard' in server_info):
            port = springboard.create_proxy(
                'login:%s' %server_num,
                server_info['springboard_info'],
                server_info)

            server_info['host'] = 'localhost'
            server_info['port'] = port

            ssh_verify_by_server(server_info,'验证',server_num)
        else:
            if( server_info['port'] != '22'):
                known_host = os.popen("ssh-keygen -F [%s]:%s" %(server_info['host'],str(server_info['port'])) )
                if (known_host.read() == ''):
                    ssh_verify('验证',server_num)
            else:
                ssh_verify('验证',server_num)
    login_cmd(server_info)

def login_cmd(server_info):
    socket5proxy = ''
    if( 'socks5proxy' in server_info ):
        socket5proxy = ' -o "ProxyCommand=nc -X 5 -x '+server_info['socks5proxy']+' %h %p"'
    login_command = "%s -p '%s' ssh %s %s@%s -p %s -o ServerAliveInterval=60 -t " %( sshpass, server_info['password'],socket5proxy, server_info['user'], server_info['host'] ,server_info['port'] )

    if( 'defaultPath' in server_info ):
        login_command = login_command+"'cd %s;bash;'" %(server_info['defaultPath'])
    else:
        login_command = login_command+"'bash;'"
    os.system(
        '''%s -p '%s' ssh %s %s@%s -p %s -t '\
        echo "\033[33m ";\
        date -R;echo '';\
        echo 内网IP:$(ifconfig |head -n 2|grep "inet addr"|cut -b 21-80);\
        echo 系统:$(head -n 1 /etc/issue) $(getconf LONG_BIT)位;\
        echo cpu:$(cat /proc/cpuinfo |grep "model name"| wc -l)核;\
        cat /proc/meminfo |grep 'MemTotal';echo 磁盘使用:;\
        df -hl;\
        echo "\033[0m";\
        ' ''' %( sshpass, server_info['password'],socket5proxy, server_info['user'], server_info['host'] ,server_info['port']),
    )
    os.system(login_command)


def proxy_ssh_verify(name,i):
    server_info = data.servers[i]
    if('springboard' in server_info):
        port = springboard.create_proxy(
            'login:%s' %i,
            server_info['springboard_info'],
            server_info)

        server_info['host'] = 'localhost'
        server_info['port'] = port
        ssh_verify_by_server(server_info,'验证',i)
        springboard.proxy_stop('login:%s' %i)
    else:
        ssh_verify(name, i)

def ssh_verify(name, i):
    server_info = data.servers[i]
    ssh_verify_by_server(server_info,name,i)

def ssh_verify_by_server(server_info,name,i):
    cmd = 'cd ;ls;'
    ssh = pexpect.spawn('ssh %s@%s  -p %s  "%s"' %(
        server_info['user'],
        server_info['host'],
        server_info['port'],
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
