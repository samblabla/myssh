#coding:utf-8
from __future__ import division

import os
import sys
import math
import paramiko
import readline
import time

import yaml
import re
from stat import S_ISDIR

import tab

import config


servers=list();

sshpass = config.sshpass
source_path = config.source_path
known_hosts = config.known_hosts
editor = config.editor
yaml_path = config.yaml_path

regex = re.compile(r'([\s\S]+?)-\d+$')#正则匹配 名字 关联批量操作
regex_cmd = re.compile(r'^(\d+):([\w\W]+)')#多台服务器操作时 判断是否只操作一台

ssh_login_cmd = re.compile(r'^(\d+) ([\w\W]{2,})')#多台服务器操作时 判断是否只操作一台

reload(sys)
sys.setdefaultencoding( "utf-8" )
cmd_cache={}
COMMANDS = ['cmd ','quit','help']
def complete(text, state):

    for cmd in COMMANDS:
        if cmd.startswith(text):
            if not state:
                return cmd
            else:
                state -= 1


# def complete_path(text,state): #自动补全
#     global ssh_complete,path_complete
#     cmd = 'cd '+path_complete+' && ls'

#     path = text
#     if text !='' and text!='./':
#         if text.rindex("/") != 0:
#             path=text[0:text.rindex("/")-1] 
#         if path !='':
#             cmd = 'cd '+path_complete+' && cd ' + path +' && ls'

#     temp = ssh_cmd_cache( ssh_complete, cmd)
#     print( temp )
#     list_file = temp.split('\n')
    
#     print('--')
#     if text !='':
#         if( text.rindex("/") !=0):
#             text =text[text.rindex("/")+1:]
#     for file_name in SS:
#         print(SS)
#         if file_name.startswith(text):
#             if not state:
#                 if(path):
#                     return path+file_name
#                 else:
#                     return file_name
#             else:
#                 state -= 1

def complete_path(text, state):#自动补全
    global ssh_complete,path_complete
    cmd = 'cd '+path_complete+' && ls -F'
    path =''
    if '/' in text:
        path = text[0:text.rindex('/')] +'/';
        sub_text = text[text.rindex('/')+1:];
        cmd = 'cd '+path_complete+' && cd ' + path +' && ls -F'
    else:
        sub_text = text
    temp = ssh_cmd_cache( ssh_complete, cmd)
    temp_list_file = temp.split('\n')
    list_file = list()
    for line in temp_list_file:
        if(line[-1] == '#' or line[-1]=='*' or line[-1]=='=' or line[-1]=='|' or line[-1]=='@'):
            list_file.append(line[0:-1])
        else:
            list_file.append(line)

    for file_name in list_file:
        if file_name.startswith(sub_text):
            if not state:
                return path+file_name
            else:
                state -= 1


# readline.set_completer(complete)
# readline.set_completer(complete_path)

# readline.set_completer()

def ssh_cmd_login(host,user,pwd,port):
    #建立ssh连接
    ssh=paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,port=port,username=user,password=pwd,compress=True)
    return ssh

def ssh_cmd(ssh,cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read()[0:-1]

def ssh_cmd_cache(ssh,cmd):
    global cmd_cache
    if( not cmd_cache.has_key(cmd) ):
        stdin, stdout, stderr = ssh.exec_command(cmd)
        cmd_cache = {cmd: stdout.read()[0:-1]}
    return cmd_cache[ cmd ]

def ssh_cd(ssh,cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd+' && pwd')
    result = stdout.read()[0:-1]
    if( result == ''):
        print('\n\33[31merror:目录不存在!!\33[0m')
        return False
    else:
        return result

def scp_login(host,user,pwd,port):
    scp=paramiko.Transport((host,port))
    #建立连接
    scp.connect(username=user,password=pwd)
    sftp=paramiko.SFTPClient.from_transport(scp)

    return sftp

def scp_upload(server_num,sftp,localFile,remoteFile):
    # print( localFile ,remoteFile )
    global servers
    
    try:

        result=sftp.put(localFile,remoteFile,printTotals)
        print ''
    except Exception, e:
        print '发生错误,尝试重连...'
        if(servers[server_num].has_key('port')):
            port = servers[server_num]['port']
        else:
            port = 22
        global scp_conns
        scp_conns[ server_num ] = scp_login(
                servers[server_num]['host'],
                servers[server_num]['user'],
                servers[server_num]['password'],
                port
                )
        scp_upload(server_num,scp_conns[ server_num ],localFile,remoteFile)

def printTotals(transferred, toBeTransferred):
    

    percent =(transferred / toBeTransferred ) *100
    # progress = '[' + ( '=' * int(percent) /2 ) +(  '' * int( percent ) /2  ) + ']'

    progress =math.floor(  int(percent) /2  );
    if( percent >10 ):
        percent = "  %.2f" %percent
    else:
        percent = "   %.2f" %percent
    msg= "%s%% [%s>%s]%s  " %(percent,'=' * int(progress) ,' ' * int(50 - progress) ,group( transferred ) )
    # msg= "%s%% [%s>%s]%d  " %(percent,'=' * int(progress) ,' ' * int(50 - progress) , transferred )
    sys.stdout.write( msg )
    sys.stdout.write( ('\b')  * len(msg))
    sys.stdout.flush()

    # if(progress == 50):
    
def group(n, sep = ','):
    s = str(abs(n))[::-1]
    groups = []
    i = 0
    while i < len(s):
        groups.append(s[i:i+3])
        i+=3
    retval = sep.join(groups)[::-1]
    if n < 0:
        return '-%s' % retval
    else:
        return retval

def check_up(server_num,sftp,ssh,localPath,remotePath,fileName,cmdPath):
    if( os.path.isdir( localPath ) ):
        os.chdir(os.path.split(localPath)[0])
        cmd = 'find ' + localPath + ' -type f | wc -l'
            # cmd = 'find ' + '/Users/sam/ssh_data/' + ' -type f | wc -l'
        for line in os.popen(cmd):
            file_num = int(line) 
        if( file_num > 15):
            # input_result = raw_input( '上传文件数量为:%d,建议压缩后再上传(输入y继续上传,输入t打包下载,输入n退出):' %file_num )
            input_result = 't'
            if( input_result == 'y'):
                up_files(sftp,localPath,remotePath )
            elif( input_result == 't'):
                global new_time
                global n
                new_time = str( new_time )
                # print( '%s_%s.tar '  %(fileName,new_time )  )

                if ( n != 0 ):
                    print '开始上传 %s_%s.tar '  %(fileName,new_time )
                else:
                    cmd = 'tar -czf %s_%s.tar %s' %( fileName,new_time , fileName)
                    os.system( cmd )    
                    print '打包完成,开始上传 %s_%s.tar '  %(fileName,new_time )
                # print( localPath+'_'+new_time+'.tar' , remotePath + fileName+'_'+new_time+'.tar' )
                # print( localPath+'.tar',remotePath + fileName+'.tar'  )
                scp_upload(server_num,sftp,localPath+'_'+new_time+'.tar',remotePath + fileName+'_'+new_time+'.tar')

                # input_result2 = raw_input( '上传完成,是否解压(y/n):' )
                input_result2 = 'y'

                if( input_result2 == 'y'):

                    cmd = 'tar -xvf %s_%s.tar'  %( fileName,new_time) 
                    print( cmd )
                    cmd = 'cd '+cmdPath+' && '+ cmd
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    result = stdout.read()[0:-1]

                    if( stdout.read()[0:-1] == '' ):
                        print( result )

                    cmd= 'rm %s_%s.tar'     %( fileName,new_time)
                    print( cmd )
                    cmd = 'cd '+cmdPath+' && '+ cmd
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                else:
                    return
            else:
                return
        else:
            up_files(sftp,localPath,remotePath )
    
    else:
        scp_upload(server_num,sftp,localPath,remotePath + fileName)


def up_files( sftp,localPath,remotePath ):

    parent=os.path.split(localPath)[1]
    for walker in os.walk(parent):
        try: 
            sftp.mkdir(os.path.join(remotePath,walker[0]))  
        except:  
            pass  
        for file in walker[2]:
            if( file != '.DS_Store' ):
                print(  os.path.join(remotePath,walker[0],file )  )
                sftp.put(os.path.join(walker[0],file),os.path.join(remotePath,walker[0],file))  



def sftp_walk(sftp,remotePath):
    #建立一个sftp客户端对象，通过ssh transport操作远程文件
    files=[]
    folders=[]
    # Copy a remote file (remotePath) from the SFTP server to the local host
    try:
        # files = sftp.listdir(remotePath) 
        # print(files)
        # print remotePath
        for f in sftp.listdir_attr(remotePath):
            if S_ISDIR( f.st_mode ):  
                folders.append(f.filename)  
            else:  
                files.append(f.filename) 


        yield remotePath,folders,files  
        for folder in folders:  
            new_path=os.path.join(remotePath,folder)  
            for x in sftp_walk(sftp,new_path):  
                yield x  
    except Exception, e:
        print e
        # print '发生错误'

def sftp_walk_time(sftp,remotePath):
    #建立一个sftp客户端对象，通过ssh transport操作远程文件
    files={}
    folders=[]
    if remotePath.split("/")[-1] =='Runtime':
        return
    if remotePath.split("/")[-1] =='ThinkPHP':
        return
    if remotePath.split("/")[-1] =='Uploads':
        return
    if remotePath.split("/")[-1] =='Pay':
        return
    if remotePath.split("/")[-1] =='Qrcode':
        return
        
    # Copy a remote file (remotePath) from the SFTP server to the local host
    try:
        # files = sftp.listdir(remotePath) 
        # print(files)
        for f in sftp.listdir_attr(remotePath):
            if S_ISDIR( f.st_mode ):  
                folders.append(f.filename)
            else:  
                # files.append(f.filename) 
                files[f.filename] = f.st_mtime

        yield remotePath,folders,files  
        for folder in folders:
            new_path=os.path.join(remotePath,folder)  
            for x in sftp_walk_time(sftp,new_path):  
                yield x  
    except Exception, e:
        print e
        # print '发生错误'
    
def check_down( sftp,ssh,remotePath,localPath,fileName ,cmdPath):#检查下载

    try:
        sftp.listdir_attr(remotePath)
        cmd = 'find ' + remotePath + ' -type f | wc -l'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        file_num = int(stdout.read()[0:-1] )
        if( file_num >15 ):
            global new_time
            new_time = str( new_time )
            input_result = raw_input( '下载文件数量为:%d,建议压缩后再下载(输入y继续下载,输入t打包下载,输入n退出):' %file_num )
            if(input_result == 'y'):
                scp_downs(sftp,remotePath,localPath)
            elif(input_result == 't'):
                if fileName == '':
                    temp=remotePath.split('/')
                    fileName = temp[ len(temp)-2]
                cmd = 'tar -czf %s_%s.tar %s' %( fileName, new_time , fileName)
                print( cmd )
                cmd = 'cd '+cmdPath+' && '+ cmd

                stdin, stdout, stderr = ssh.exec_command(cmd)

                if( stdout.read()[0:-1] == '' ):
                    print( '打包完成,开始下载 %s_%s.tar '  %(fileName ,new_time) )
                    # scp_down(sftp,remotePath + '_'+new_time+ '.tar',localPath+fileName+'_'+new_time+'.tar')
                    # print( cmdPath +'/'+ fileName + '_'+new_time+ '.tar' )
                    scp_down(sftp,cmdPath + '/'+ fileName + '_'+new_time+ '.tar',localPath+fileName+'_'+new_time+'.tar')

                else:
                    print '操作失败'
            elif(input_result == 'n'):
                return
            else:
                return
        else:
            scp_downs(sftp,remotePath,localPath)

    except Exception,e:
        scp_down(sftp,remotePath,localPath+fileName)

def scp_downs(sftp,remotePath,localPath):
        #  recursively download a full directory  
        #  Harder than it sounded at first, since paramiko won't walk  
        #  
        # For the record, something like this would gennerally be faster:  
        # ssh user@host 'tar -cz /source/folder' |  

        try:
            print('下载 %s 中 ...' %remotePath)
            sftp.listdir_attr(remotePath)

            parent=os.path.split(remotePath)[1]

            sftp.chdir(os.path.split(remotePath)[0])
            try:  
                os.mkdir(localPath)  
            except:
                pass  
            for walker in sftp_walk(sftp,parent):  
                try:  
                    os.mkdir(os.path.join(localPath,walker[0]))  
                except:
                    pass  
                for file in walker[2]:
                    print( ' '+os.path.join(walker[0],file) )
                    sftp.get(os.path.join(walker[0],file),os.path.join(localPath,walker[0],file), printTotals)
                    print('')
        except Exception,e:
            print( e )

def show_remote_file(sftp,remotePath,server_num):
    file_info ={}
    file_nums =0 
    sftp.listdir_attr(remotePath)

    parent=os.path.split(remotePath)[1]

    sftp.chdir(os.path.split(remotePath)[0])
 
    for walker in sftp_walk_time(sftp,parent):  
        for file in walker[2]:
            file_nums += 1
            msg = '%d:正在扫描文件 %d' %(server_num,file_nums)
            sys.stdout.write(msg + ('\b')  * len(msg) )
            sys.stdout.flush()

            file_info[os.path.join(walker[0],file)] = walker[2][file]
    print('%d:扫描完成' %server_num)

    return file_info

def scp_down(sftp,remoteFile,localFile):

    # Copy a remote file (remotePath) from the SFTP server to the local host
    try:
        result=sftp.get(remoteFile,localFile, printTotals )
        print('')
    except Exception, e:
        print e
        print '发生错误'


def relation_add( l ,i ,sign):
    global relation 
    result_str =''

    if( regex.match( l['name'] ) != None ):
        relation_key = regex.match( l['name'] ).group(1)

        if( len(sys.argv) >1 and sys.argv[1] == 'all' ):
            result_str = sign+'\33[41m%s\33[0m:%s(%s)\n' %(i, l['name'],l['host'] )
        else:
            if( not relation.has_key( relation_key  ) ):
                result_str = sign+'\33[41m%s\33[0m:%s(%s) <<%s>>\n' %(i, l['name'],l['host'] ,relation_key )
        
        if( not relation.has_key( relation_key  ) ):

            relation[ relation_key ] = list()
            

        relation[ relation_key ].append(i) 


        return result_str
    else:
        return sign+'%s:%s(%s)\n' %(i, l['name'],l['host']) 

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
def list_del_empty(data):
    while '' in data:
        data.remove('')
    return data

def ssh_cmd_func(server_num,result,p_cmd,ssh_conns,source_path,n):
    global paths,cmds
    server_num = int(server_num)
    server_info = result[ server_num ]

    print ('\33[34m%d:\33[31m%s(%s)\33[0m' %(server_num,server_info['name'],server_info['host']) )

    cmd = p_cmd

    if( p_cmd[0:2] == 'cd'):
        cmd = 'cd '+paths[server_num]+' && '+ cmd
        # print(cmd)
        temp_path = ssh_cd(ssh_conns[ server_num ],cmd )
        if( temp_path ):
            paths[server_num] = temp_path 
        else:
            return 'notpath'

    elif( p_cmd[0:2] ==  'up' ):
        cmds = cmd.split(' ')
        fileName = cmds[1].split('/')
        fileName[ len(fileName)-1]

        # scp_upload(scp_conns[ server_num ],'ssh_data/'+cmds[1],paths[server_num]+'/'+fileName[ len(fileName)-1])
        # print source_path+'/up/'+cmds[1]
        check_up(server_num, scp_conns[ server_num ],ssh_conns[ server_num ],source_path+'up/'+cmds[1],paths[server_num]+'/', fileName[ len(fileName)-1] ,paths[server_num])
    # elif(p_cmd[0:5] =='downs'):
    #     cmds = cmd.split(' ')
    #     fileName = cmds[1].split('/')

    #     os.system( 'mkdir -p /Users/sam/ssh_data/'+server_info['name']+'/' )
    #     scp_downs(scp_conns[ server_num ],paths[server_num] + '/' + cmds[1],'/Users/sam/ssh_data/'+server_info['name'])

    elif( p_cmd[0:4] == 'down' ):
        cmds = cmd.split(' ')
        fileName = cmds[1].split('/')
        os.system( 'mkdir -p "'+source_path+server_info['name']+'/"' )

        check_down(
            scp_conns[ server_num ],
            ssh_conns[ server_num ],
            paths[server_num] + '/' + cmds[1],
            source_path+server_info['name']+'/' ,
            fileName[ len(fileName)-1],paths[server_num] )
        os.system('open "'+source_path+server_info['name']+'/"')

        # scp_downs(scp_conns[ server_num ],paths[server_num] + '/' + cmds[1],'/Users/sam/ssh_data/'+server_info['name']+'/' , fileName[ len(fileName)-1])
    else:
        cmd = 'cd '+paths[server_num]+' && '+ cmd
        # print(cmd)
        cmds[ n ] = ssh_cmd(ssh_conns[ server_num ], cmd)
        print( cmds[ n ] )





f_pubssh = open( known_hosts,"r")

local_pubssh = []
for line in f_pubssh.readlines():
    new_line = line.split(' ')[0];

    if( len( new_line.split(',') ) > 1 ):
        for x_ip in new_line.split(','):
             local_pubssh.append(  x_ip  )
    else:
        local_pubssh.append(  new_line  )
# print( local_pubssh )
if( len(sys.argv) >1 and sys.argv[1] == 'edit'):
    os.system("open -a "+editor+' ' +sys.path[0]+ '/'+yaml_path)

elif( len(sys.argv) >1 and sys.argv[1] == 'self'):
    os.system("open -a "+editor+' '+sys.path[0]+'/'+sys.argv[0])
else:
    f = open( sys.path[0]+'/'+yaml_path,'r')
    result = list()
    relation ={}
    temp_result = yaml.load( f )
    group_code_list ={}
    f.close()
    if( temp_result == None ):
        show_str = '= =! 还没有服务器\nmyssh add      使用命令添加服务器信息'
    else:
        show_str = '服务器列表:\n'
        
        i = 0
        


        for v in temp_result:
            # v['name'] = v['name'].encode('utf-8')
            if( v.has_key('group') ):  #分组
                # \33[40m
                # print('\33[32m')
                if(v.has_key('code')):
                    show_str += '\33[42m\33[30m  %s [%s] \33[0m\n' % ( v['name'] ,v['code'] ) 
                    # group_code_list
                    group_code_list[v['code']]=list()
                else:
                    show_str += '\33[42m\33[30m  %s  \33[0m\n' % ( v['name'] ) 
                for l in v['group']:
                    # l['name'] = l['name'].encode('utf-8')

                    result.append( l )


                    show_str += relation_add(l,i,'\33[42m \33[0m ')
                    if(v.has_key('code')):
                       group_code_list[v['code']].append(i)

                    i+=1
                show_str +='\n'
            else:
                result.append( v )
                show_str += relation_add(v,i,'\33[40m \33[0m ')
                i+=1

        servers = result
        if( len(sys.argv) >1 and  sys.argv[1] == "verify" ):
            for server_info in result:
                if server_info['host'] not in local_pubssh:
                    if(server_info.has_key('port')):
                        port = server_info['port']
                    else:
                        port = 22
                    print('\n\33[31m%s(%s)还没有添加公钥,输入 yes后 ctrt+c退回 \33[0m\n\n' %(
                        server_info['name'],
                        server_info['host'] ))
                    print "ssh %s@%s  -p %s" %(
                        server_info['user'],
                        server_info['host'],
                        port )
                    os.system("ssh %s@%s  -p %s" %(
                        server_info['user'],
                        server_info['host'],
                        port ))

            
            exit()

        for x in relation:
            # print(  '\33[31m' + str( len( relation[x] ) ) + '\33[0m' )
            # exit()
            # print( relation[x])
            
            show_str = show_str.replace( '<<%s>>' %x, '    \33[41m ' + str( len( relation[x] ) ) + '台 \33[0m\33[45m %s \33[0m' %' | '.join(str(i) for i in relation[x])  )
        server = ''
        while(1):
            readline.set_completer(complete)

            global sever
            if(server == 'help'):
                help_str='''
\33[33mcmd\33[0m    服务器编号[...] 如 cmd 1 2 3 ,可操作多台服务器
\33[33mcmd -l\33[0m 服务器编号  操作与服务器有关联的多台服务器 关联规则 服务器名-数字
\33[33mcmd -g\33[0m 服务器编号  操作分组中的多台服务器,需要配置分组code
    \33[33mup\33[0m     上传文件 如 up 本地文件名 
    \33[33mdown\33[0m   下载文件 如 down 服务器文件名 本地文件名(可选)
    \33[33msync\33[0m   同步文件 "sync 服务器id > 被同步的服务器id(多个使用空格分隔)" 如 sync 1 > 2 3

    多台操作时 使用 "服务器id:操作指令" 可操作单台服务器 如 1:ls

\33[33mexit\33[0m   返回上级操作
\33[33mquit\33[0m   退出程序
                '''
                print( help_str )
            else:
                print( show_str )
            try:
                server = raw_input("输入服务器编号(help 帮助):")
            except KeyboardInterrupt:
                print('')
                server = 'quit'
                pass
            # server = raw_input("输入服务器编号(help 帮助):")
            if(server =='help'):
                continue
            elif(server == 'quit'):
                exit()
            elif(server.find('cmd ') != -1):
                

                server_nums =  server.split(' ')
                # print '\n\33[31m 可使用命令up down 上传下载 \33[0m'
                # print '\n\33[31m 正在连接服务器 ... \33[0m'
                server_nums = list_del_empty( server_nums )
                ssh_conns={}
                scp_conns={}
                paths={}

                if( server.find('cmd -l') != -1 ):
                    server_list = relation[   regex.match( result[ int( server_nums[2] ) ]['name'] ).group(1)  ]
                    
                elif( server.find('cmd -g') != -1 ):
                    server_list = group_code_list[ server_nums[2] ]
                else:
                    server_list = server_nums[1:]
                    server_list = map(eval, server_list)
                    # server_num = int( server_list[0] )

                server_info = result[ int( server_list[0] ) ]
                server_len =len( server_list )

                for server_num in server_list:        

                    server_num = int(server_num)
                    server_info = result[ server_num ]
                    print '\33[34m%d:\33[31m正在连接：%s(%s) \33[0m' %(server_num,server_info['name'],server_info['host'])
                    # print '\n\33[31m正在连接：%s(%s) \33[0m' %(server_info[3],server_info[0])
                    if(server_info.has_key('port')):
                        port = server_info['port']
                    else:
                        port = 22
                    ssh_conns[ server_num ] = ssh_cmd_login(
                        server_info['host'],
                        server_info['user'],
                        server_info['password'],
                        port
                        )
                    
                    # print '\n\33[31m正在执行命令...\33[0m\n'
                    scp_conns[ server_num ] = scp_login(
                        server_info['host'],
                        server_info['user'],
                        server_info['password'],
                        port
                        )
                    
                    if( server_info.has_key('defaultPath') ):
                        temp_path =ssh_cd( ssh_conns[ server_num ] ,'cd ' + server_info['defaultPath'])
                        if( temp_path ):
                            paths[server_num] = temp_path
                        else:
                            paths[server_num] = ssh_cd(
                                ssh_conns[ server_num ],
                                'cd ./' )
                    else:
                        paths[server_num] = ssh_cd(
                            ssh_conns[ server_num ],
                            'cd ./' )

                if( server_info.has_key('description') ):
                    print( '\33[32m' + server_info['description'].replace('#',' \33[35m#').replace('\\n ','\33[32m\n') +'\33[0m\n' )

                readline.set_completer(complete_path)
                while(1):
                    # os.chdir('/Users/sam')
                    cmds={}

                    i = 0
                    for server_num in server_list:
                        i+=1
                        server_num = int(server_num)
                        server_info = result[ server_num ]

                        if(server_len == i):
                            ssh_complete = ssh_conns[ server_num ]
                            path_complete = paths[ server_num ]
                            
                            try:
                                p_cmd = raw_input( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m ' %(
                                    server_num,server_info['user'],
                                    server_info['name'],
                                    server_info['host'],
                                    paths[server_num] ))
                            except KeyboardInterrupt:
                                p_cmd ='exit'
                                print('')
                        else:

                            print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m ' %(
                                server_num,
                                server_info['user'],
                                server_info['name'],
                                server_info['host'],
                                paths[server_num] ))


                    if( p_cmd == 'exit'):
                        for server_num in server_list:
                            server_num = int(server_num)
                            print '\33[31m正在断开连接：%s(%s) \33[0m' %(
                                result[ server_num ]['name'],
                                result[ server_num ]['host'] )

                            ssh_conns[ server_num ].close()
                            scp_conns[ server_num ].close()
                        break
                    if( p_cmd ==''):
                        continue

                    if( p_cmd == 'quit'):
                        exit()
                    n = 0
                    if( p_cmd[0:3] =='rm '):
                        certain = raw_input( '确定要执行删除命令吗?(y/n):' )
                        if( certain !='y'):
                            continue

                    if(p_cmd[0:5] =='sync '):
                        sync_info = p_cmd.split( '>' )
                        client_file={}
                        add_file ={}
                        # print(sync_info[0])
                        # print(sync_info[1])
                        temp_master  =  sync_info[0].split(' ')
                        temp_master = list_del_empty( temp_master )

                        master_server = int( temp_master[1] )
                        if  len(sync_info) > 1 :

                            client_server = sync_info[1].split(' ')
                            client_server = list_del_empty( client_server )

                        else:
                            client_server =list()
                            client_server.extend( server_list )
                            client_server.remove( master_server )


                        master_file = show_remote_file(
                            scp_conns[ master_server ],
                            paths[ master_server ] , master_server)
                         
                        master_remote_path = paths[master_server]

                        is_all_sync_file = False
                        for server_num in client_server:
                            server_num = int(server_num)
                            client_file[server_num] = show_remote_file(
                                scp_conns[ server_num ],
                                paths[ server_num ] , server_num)
                            server_info = result[ server_num ]
                            print( '\33[34m%d:\33[31m%s(%s)\33[0m' %(
                                server_num,server_info['name'],
                                server_info['host'] ))

                            add_file[ server_num ] =list()
                            is_sync_file= False
                            
                            for file_name in master_file:
                                if( client_file[server_num].has_key(file_name)):
                                    if( master_file[ file_name ] > client_file[ server_num ][ file_name ]):

                                        x = time.localtime( master_file[ file_name ] )
                                        mtime = time.strftime('%Y-%m-%d %H:%M:%S',x)
                                        print( "  更新: %s 修改时间:%s" %( file_name, mtime) )
                                        add_file[ server_num ].append(file_name) 
                                        is_all_sync_file =True
                                        is_sync_file = True
                                else:
                                    x = time.localtime( master_file[ file_name ] )
                                    mtime = time.strftime('%Y-%m-%d %H:%M:%S',x)

                                    print( "  添加: %s 修改时间:%s"%( file_name,  mtime) )
                                    add_file[ server_num ].append(file_name) 
                                    is_all_sync_file =True
                                    is_sync_file = True
                            if( not is_sync_file ):
                                print('  没有需要同步的文件')

                        if( not is_all_sync_file ):
                            # print('没有需要同步的文件')
                            continue
                        certain = raw_input('确定要同步吗?(y/n):')
                        if( certain !='y'):
                            continue
                        else:
                            files_list =list()
                            for server_num in add_file:

                                client_remote_path = paths[server_num]

                                # os.system( 'mkdir -p "'+'/Users/sam/ssh_data/'+result[master_server]['name']+'-SYNC'+'/"' )
                                # print( add_file)
                                
                                server_info = result[ master_server ]
                                files_list.extend(add_file[ server_num ])

                            files_list = list( set(files_list) )
                            print( '\33[34m%d:\33[31m%s@%s(%s)\33[0m 下载中' %(
                                master_server,server_info['user'],
                                server_info['name'],
                                server_info['host']))

                            for file_name in files_list:
                                # print( remote_path ,file_name )
                                # print '/Users/sam/ssh_data/'+result[master_server]['name']+'-SYNC/' +file_name[0:file_name.rindex('/')]
                                os.system('mkdir -p "'+ source_path+result[master_server]['name']+'-SYNC/' +file_name[0:file_name.rindex('/')] + '/"')
                                # print('mkdir -p "'+ '/Users/sam/ssh_data/'+result[master_server]['name']+'-SYNC/' +file_name[0:file_name.rindex('/')] + '/"')

                                # print( master_remote_path +'/'+file_name[file_name.index('/')+1:],'/Users/sam/ssh_data/'+result[master_server]['name']+'-SYNC/'+file_name )
                                # print('mkdir -p "'+ '/Users/sam/ssh_data/'+result[master_server]['name']+'-SYNC/' +file_name[0:file_name.rindex('/')] + '/"')
                                
                                print(' ' + file_name[file_name.index('/')+1:])
                                scp_down(
                                    scp_conns[ master_server ],
                                    master_remote_path +'/'+file_name[file_name.index('/')+1:],
                                    source_path+result[master_server]['name']+'-SYNC/'+file_name )

                            for server_num in add_file:
                                server_info = result[ server_num ]
                                print( '\33[34m%d:\33[31m%s@%s(%s)\33[0m 上传中' %(
                                    server_num,server_info['user'],
                                    server_info['name'],
                                    server_info['host']))

                                for file_name in add_file[server_num]:
                                    # print( file_name)
                                    # print(client_remote_path +'/'+file_name[  file_name.index('/') :  file_name.rindex('/') ] + '/')  
                                    if(file_name.count('/') > 1):
                                        # print( client_remote_path +'/' )
                                        # print( file_name[ file_name.index('/'):file_name.rindex('/')] + '/' )
                                        # print( client_remote_path +file_name[ file_name.index('/'):file_name.rindex('/')] + '/' )
                                        # print( client_remote_path +file_name[ file_name.index('/'):file_name.rindex('/')] + '/' )
                                        try:
                                            cmd = 'mkdir -p "' + client_remote_path + file_name[ file_name.index('/'):file_name.rindex('/')] + '/"'
                                            # print(cmd)
                                            ssh_cmd(ssh_conns[ server_num ], cmd)
                                            # scp_conns[ server_num ].mkdir(client_remote_path +file_name[ file_name.index('/'):file_name.rindex('/')] + '/')  

                                            # scp_conns[ server_num ].mkdir(client_remote_path +file_name[ file_name.index('/'):file_name.rindex('/')] + '/')  
                                        except Exception,e:
                                            pass
                                    print(' ' + file_name[file_name.index('/')+1:])
                                    scp_upload(
                                        server_num,
                                        scp_conns[ server_num ],
                                        source_path+result[master_server]['name']+'-SYNC/'+file_name,
                                        client_remote_path +'/'+file_name[file_name.index('/')+1:] )


                        continue

                    if(p_cmd[0:7] =='script '):
                        certain = raw_input( '确定要执行脚本命令吗?(y/n):' )
                        if( certain !='y'):
                            continue
                        else:
                            p_cmd = p_cmd.split(' ')
                            # print(source_path+'script/'+p_cmd[1])
                            scripts = open( source_path+'script/'+p_cmd[1] ,"r")
                            script_err =''
                            for script in scripts.readlines():
                                p_cmd = script.strip('\n')
                                if( p_cmd[0:1] =='#' ):
                                    continue
                                cmds={}
                                i = 0
                                n = 0
                                server_num_arr = regex_cmd.match(p_cmd)


                                if(server_num_arr):
                                    if( not paths.has_key( int( server_num_arr.group(1) ) ) ):
                                        script_err ='notpath'
                                        print('您不能操作未连接的服务器')
                                        break
                                    print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m%s' %(
                                        int( server_num_arr.group(1) ),
                                        server_info['user'],
                                        server_info['name'],
                                        server_info['host'],
                                        paths[ int( server_num_arr.group(1) ) ],
                                        p_cmd ))
                                else:
                                    for server_num in server_list:
                                        i+=1
                                        server_num = int(server_num)
                                        server_info = result[ server_num ]

                                        if(server_len == i):
                                            ssh_complete = ssh_conns[ server_num ]
                                            path_complete = paths[ server_num ]
                                            print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m%s' 
                                                %( server_num,server_info['user'],
                                                    server_info['name'],
                                                    server_info['host'],
                                                    paths[server_num],
                                                    p_cmd )  )
                                        else:
                                            print( '\33[34m%d:\33[33m%s@%s(%s):%s#\33[0m' 
                                                %( server_num,server_info['user'],
                                                    server_info['name'],
                                                    server_info['host'],
                                                    paths[server_num] )  )
                                
                                if( 'notpath' == script_err ):
                                    break


                                new_time = time.time()
                                if( server_num_arr ):
                            
                                    script_err = ssh_cmd_func( 
                                        int(server_num_arr.group(1)),
                                        result,server_num_arr.group(2),
                                        ssh_conns,
                                        source_path,
                                        n) 
                                    if( 'notpath' == script_err):
                                        print('\33[31m脚本停止执行!!\33[31m')
                                        break
                                else:
                                    for server_num in server_list:
                                        ssh_cmd_func(
                                            server_num,
                                            result,
                                            p_cmd,
                                            ssh_conns,
                                            source_path,
                                            n ) 

                                        if( 'notpath' == script_err ):
                                            print('\33[31m脚本停止执行!!\33[31m')
                                            break
                                        n+=1
                                    if( 'notpath' == script_err ):
                                        break

                                if( 'notpath' == script_err ):
                                    break
                                if( p_cmd[0:2] != 'cd' and p_cmd[0:2] != 'up' and p_cmd[0:4] != 'down' ):
                                    for x in range(n-1):
                                        if( cmds[x] != cmds[x+1] ):
                                            print( '\33[34m执行结果不一致\33[0m' )
                                            break


                            continue


                    new_time = time.time()

                    server_num_arr = regex_cmd.match(p_cmd) 
                    if( server_num_arr ):
                        server_num = server_num_arr.group(1)
                        if( not paths.has_key( int( server_num ) ) ):
                            print('您不能操作未连接的服务器')
                            continue
                        p_cmd = server_num_arr.group(2)
                        if( p_cmd[0:3] =='rm '):
                            certain = raw_input( '确定要执行删除命令吗?(y/n):' )
                            if( certain !='y'):
                                continue
                        ssh_cmd_func(
                            server_num,
                            result,
                            p_cmd,
                            ssh_conns,
                            source_path,
                            n )
                    else:
                        for server_num in server_list:
                            ssh_cmd_func(
                                server_num,
                                result,
                                p_cmd,
                                ssh_conns,
                                source_path,
                                n )
                            n+=1    

                    if( p_cmd[0:2] != 'cd' and p_cmd[0:2] != 'up' and p_cmd[0:4] != 'down' ):
                        for x in range(n-1):
                            if( cmds[x] != cmds[x+1] ):
                                print( '\33[34m执行结果不一致\33[0m' )
                                break


            else:
                login_cmd = ''
                if( not is_number( server ) ):
                    server_arr = ssh_login_cmd.match(server)
                    if( not server_arr ):
                        continue
                    server_num = int( server_arr.group(1) )
                    login_cmd = server_arr.group(2)+';'
                else:
                    server_num = int(server)

                server_info = result[ server_num ]

                print u'\n\33[31m正在连接：%s(%s) \33[0m' %( server_info['name'],server_info['host'] ) 
                
                if( server_info.has_key('description') ):
                    # print( server_info['description'] )
                    print( '\33[32m' + server_info['description'].replace('#',' \33[35m#').replace('\\n ','\33[32m\n') +'\33[0m\n' )
                # print( '\n\33[32m'  )
                if(server_info.has_key('port')):
                    port = server_info['port']
                else:
                    port = '22'
                if( server_info.has_key('defaultPath') ):
                    # print('''/Users/sam/SamTool/sshpass-1.05/sshpass -p %s ssh %s@%s -t 'head -n 1 /etc/issue;echo cpu:$(cat /proc/cpuinfo |grep "model name"| wc -l)核;echo 内存: $(cat /proc/meminfo |grep 'MemTotal'|awk '{print $2,$3}');cd %s;bash' ''' %( server_info['password'], server_info['user'], server_info['host'] ,server_info['defaultPath']) )

                    os.system('''%s -p '%s' ssh %s@%s -p %s -t '\
                    	echo "\033[33m ";\
                    	date -R;echo '';\
                    	echo 内网IP:$(ifconfig |head -n 2|grep "inet addr"|cut -b 21-80);\
                    	echo 系统:$(head -n 1 /etc/issue) $(getconf LONG_BIT)位;\
                    	echo cpu:$(cat /proc/cpuinfo |grep "model name"| wc -l)核;\
                    	cat /proc/meminfo |grep 'MemTotal';echo 磁盘使用:;\
                    	df -hl;\
                    	echo "\033[0m";\
                    	' ''' %( sshpass, server_info['password'], server_info['user'], server_info['host'] ,port) )
                    
                    os.system("%s -p '%s' ssh %s@%s -p %s -o ServerAliveInterval=60 -t  'cd %s;%sbash;'" %( sshpass, server_info['password'], server_info['user'], server_info['host'] ,port,server_info['defaultPath'] ,login_cmd) )

                else:

                    os.system("%s -p '%s' ssh %s@%s  -o ServerAliveInterval=60 -p %s" %( sshpass, server_info['password'], server_info['user'], server_info['host'] ,port) )

