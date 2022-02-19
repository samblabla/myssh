#coding:utf-8
import paramiko

import data
import common
import springboard

import socks

def login(host,user,pwd,port,server_info):
    #建立ssh连接
    ssh=paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    

    if( 'socks5proxy' in server_info ):
        socks5proxy = server_info['socks5proxy'].split(":")
        sock=socks.socksocket()
        sock.set_proxy(
            proxy_type=socks.SOCKS5,
            addr=socks5proxy[0],
            port=int(socks5proxy[1])
        )
        sock.connect((host, port))
        ssh.connect(host,port=port,username=user,password=pwd,compress=True, sock=sock)
    else:
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
    if 'springboard_info' in data.servers[server_num]:
        port = springboard.create_proxy(
            'ssh:%s' %server_num,
            data.servers[server_num]['springboard_info'],
            data.servers[server_num])

        data.ssh_conns[ server_num ] = login(
            'localhost',
            data.servers[server_num]['user'],
            data.servers[server_num]['password'],
            port,
            {}
            )
    else:

        data.ssh_conns[ server_num ] = login(
            data.servers[server_num]['host'],
            data.servers[server_num]['user'],
            data.servers[server_num]['password'],
            data.servers[server_num]['port'],
            data.servers[server_num]
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