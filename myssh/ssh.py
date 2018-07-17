#coding:utf-8
import paramiko

import data
import common
from sshtunnel import SSHTunnelForwarder



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
    except (Exception) as e:
        print('发生错误,尝试重连...',e)

        create_conn(server_num)
        return cmd(server_num,cmd_str)
    return stdout.read()[0:-1].decode()

def cmd_cache(server_num,cmd_str):
    if not server_num in data.cmd_cache:
        data.cmd_cache[server_num] = {}
    
    if( not cmd_str in data.cmd_cache[server_num] ):
        result = cmd(server_num,cmd_str)
        data.cmd_cache[server_num] = {cmd_str: result}
    return data.cmd_cache[server_num][ cmd_str ]


def cd(server_num,cmd_str):
    result = cmd(server_num,cmd_str+' && pwd')
    if( result == ''):
        print('\33[34m%d:\33[0merror:目录不存在!!' %server_num)
        return False
    else:
        return result



def create_conn(server_num):
    proxy_name ='ssh:%s' %server_num

    if 'springboard_info' in data.servers[server_num]:
        if proxy_name in data.proxy_conns:
            data.proxy_conns[proxy_name].stop()
        springboard_info = data.servers[server_num]['springboard_info']
        data.proxy_conns[proxy_name] = SSHTunnelForwarder(
           (springboard_info['host'], springboard_info['port']),
            ssh_username=springboard_info['user'],
            ssh_password=springboard_info['password'],
            remote_bind_address=(data.servers[server_num]['host'], data.servers[server_num]['port']),
        )
        
        data.proxy_conns[proxy_name].start()

        data.ssh_conns[ server_num ] = login(
            '127.0.0.1',
            data.servers[server_num]['user'],
            data.servers[server_num]['password'],
            data.proxy_conns[proxy_name].local_bind_port
            )
    else:

        data.ssh_conns[ server_num ] = login(
            data.servers[server_num]['host'],
            data.servers[server_num]['user'],
            data.servers[server_num]['password'],
            data.servers[server_num]['port']
            )



def show_remote_file(server_num,remotePath):
    getdir_cmd = '''
function getdir(){
    for t_element in `ls $1 --full-time|awk '{if(NR!=1) print}'|awk '{print $9"❂"$6"."$7}'`
    do 
        local element=$t_element
        local arr=(${element//❂/ })
        dir_or_file=$1"/"${arr[0]}
        if [ -d $dir_or_file ]
            then 
                getdir $dir_or_file
        else
            echo $dir_or_file' '${arr[1]}
        fi  
    done
}
getdir .
'''
    temp_file_info = cmd(server_num, 'cd '+remotePath+' &&'+getdir_cmd)
    file_info = {}
    if len(temp_file_info)>0:
        temp_folder= remotePath.split('/')
        folder_name = temp_folder[len(temp_folder)-1]
        for i in temp_file_info.split('\n'):
            temp_i = i.split(' ')
            temp_time = temp_i[1].split('.')
            file_path =u''+folder_name+ temp_i[0][1:]
            file_info[ file_path ] = common.strToTimestamp(temp_time[0]+' '+temp_time[1])

    print('%d:扫描完成' %server_num)

    return file_info