#coding:utf-8
import os
version = '0.3.2'
# sshpass路径
sshpass = 'sshpass'

#多服务器操作下载上传资源目录
source_path = os.path.expanduser('~')+"/myssh_files/"

#使用编辑器打开文体,linux自动使用vim
editors = [
  '/Applications/Sublime Text 2.app',
  '/Applications/Visual Studio Code.app'
  ]

#yaml配置文体地址,只支持当对路径
yaml_path = os.path.expanduser('~')+'/.myssh/myssh.yml'

yaml_demo_content = '''- name: 本地
  group:
    - 
      host: 10.211.55.6
      user: root
      password: 123456
      name: 本地CentOS
      defaultPath: /home/
      port: 22
      description: >
        这是一个描述
    - 
      host: 114.92.128.231
      user: sam
      password: 123456
      name: 联想ubuntu
      port: 11773


-
  name: app
  group:
  -
    host: 192.168.0.100
    user: root
    password: 123456
    name: APP推送服务器-1
    defaultPath: /var/local/
  -
    host: 192.168.0.101
    user: root
    password: 123456
    name: APP推送服务器-2
    defaultPath: /var/local/


- name: v9直播室
  code: web
  group:
  -
    host: 192.168.0.100
    user: root
    password: 123456
    name: web-1
    defaultPath: /var/local/
  -
    host: 192.168.0.100
    user: root
    password: 123456
    name: web-2
    defaultPath: /var/local/
  -
    host: 192.168.0.100
    user: root
    password: 123456
    name: a.com
    defaultPath: /var/local/


- 
  host: 10.211.55.6
  user: root
  password: 123456
  name: 本地CentOS
  defaultPath: /home/
  port: 22
  description: >
    这是一个描述 '''