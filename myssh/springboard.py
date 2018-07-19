#coding:utf-8
from sshtunnel import SSHTunnelForwarder
import data
import time
import os
import json
import config

def create_proxy(proxy_name,proxy_info,remote_info):
    if proxy_name[0:6] == 'login:' and proxy_name in data.proxy_conns:
        return data.proxy_conns[proxy_name].local_bind_port

    proxy_stop(proxy_name)
    
    if proxy_name in data.proxy_conns:
        data.proxy_conns.pop(proxy_name)
    data.proxy_conns[proxy_name] = SSHTunnelForwarder(
        (proxy_info['host'], proxy_info['port']),
            ssh_username=proxy_info['user'],
            ssh_password=proxy_info['password'],
            remote_bind_address=(remote_info['host'], remote_info['port']),
        )
    data.proxy_conns[proxy_name].start()
    port = data.proxy_conns[proxy_name].local_bind_port
    if proxy_name[0:6] == 'login:':
        proxy_known_hosts = read_proxy_cache()
        proxy_known_hosts["[%s]:%s" %('localhost',port)] = 0
        write_proxy_cache(proxy_known_hosts)
    
    return port


def read_proxy_cache():
    if os.path.exists(config.myssh_path+'proxy_known_hosts.json'):
        f = open(config.myssh_path+'proxy_known_hosts.json','r')
        content = f.read()
        proxy_known_hosts=json.loads(content)
        f.close()
    else:
        proxy_known_hosts = {}
    return proxy_known_hosts

def write_proxy_cache(proxy_known_hosts):
    content = json.dumps(proxy_known_hosts)
    f = open(config.myssh_path+'proxy_known_hosts.json', 'w') 
    f.write(content)
    f.close()

def clear_proxy_cache():
    proxy_known_hosts = read_proxy_cache()
    for key in proxy_known_hosts:
        os.popen("ssh-keygen -R '%s'" %key )
    write_proxy_cache({})

def proxy_stop(proxy_name):
    if proxy_name in data.proxy_conns:
        if proxy_name[0:6] == 'login:':
            key = "[%s]:%s" %(
                'localhost',
                str(data.proxy_conns[proxy_name].local_bind_port)
            )

            os.popen("ssh-keygen -R '%s'" %key )
            proxy_known_hosts = read_proxy_cache()
            proxy_known_hosts.pop(key)
            write_proxy_cache(proxy_known_hosts)

        data.proxy_conns[proxy_name].stop()
