#coding:utf-8
import paramiko

import data

def login(host,user,pwd,port):
    #建立ssh连接
    ssh=paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,port=port,username=user,password=pwd,compress=True)
    return ssh

def cmd(server_num,cmd_str):

    ssh = data.ssh_conns[server_num]
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd_str)
    except Exception, e:
        print '发生错误,尝试重连...'
        create_conn(server_num)

        return cmd(server_num,cmd_str)
    return stdout.read()[0:-1]

def cmd_cache(server_num,cmd_str):
    if( not data.cmd_cache.has_key(cmd_str) ):
        result = cmd(server_num,cmd_str)
        data.cmd_cache = {cmd_str: result}
    return data.cmd_cache[ cmd_str ]


def cd(server_num,cmd_str):
    result = cmd(server_num,cmd_str+' && pwd')
    if( result == ''):
        print('\n\33[31merror:目录不存在!!\33[0m')
        return False
    else:
        return result



def create_conn(server_num):
    if(data.servers[server_num].has_key('port')):
        port = data.servers[server_num]['port']
    else:
        port = 22
    data.ssh_conns[ server_num ] = login(
        data.servers[server_num]['host'],
        data.servers[server_num]['user'],
        data.servers[server_num]['password'],
        port
        )