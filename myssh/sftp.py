#coding:utf-8
import paramiko
import math
import sys

import data



def login(host,user,pwd,port):
    scp=paramiko.Transport((host,port))
    #建立连接
    scp.connect(username=user,password=pwd)
    sftp=paramiko.SFTPClient.from_transport(scp)

    return sftp

def upload(server_num,localFile,remoteFile):
    sftp = data.scp_conns[ server_num ]
    try:

        result=sftp.put(localFile,remoteFile,printTotals)
        print ''
    except Exception, e:
        if str(e) == 'division by zero':
            return
        # print str(e)
        print '发生错误,尝试重连...'

        create_conn(server_num)

        upload(server_num,localFile,remoteFile)


def down(server_num,remoteFile,localFile):
    sftp = data.scp_conns[ server_num ]
    # Copy a remote file (remotePath) from the SFTP server to the local host
    try:
        result=sftp.get(remoteFile,localFile, printTotals )
        print('')
    except Exception, e:
        if str(e) == 'division by zero':
            return
        print e
        print '发生错误,尝试重连...'

        create_conn(server_num)
        
        down(server_num,remoteFile,localFile)

def downs(server_num,remotePath,localPath):
    sftp = data.scp_conns[ server_num ]
    
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
        if str(e) == 'division by zero':
            return
        # print e
        print '发生错误,尝试重连...'

        create_conn(server_num)

        downs(server_num,remotePath,localPath)


def sftp_walk(sftp,remotePath):
    #建立一个sftp客户端对象，通过ssh transport操作远程文件
    files=[]
    folders=[]
    # Copy a remote file (remotePath) from the SFTP server to the local host
    try:
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
        for f in sftp.listdir_attr(remotePath):
            if S_ISDIR( f.st_mode ):  
                folders.append(f.filename)
            else:  
                files[f.filename] = f.st_mtime

        yield remotePath,folders,files  
        for folder in folders:
            new_path=os.path.join(remotePath,folder)  
            for x in sftp_walk_time(sftp,new_path):  
                yield x  
    except Exception, e:
        print e
        # print '发生错误'

def create_conn(server_num):
    if(data.servers[server_num].has_key('port')):
        port = data.servers[server_num]['port']
    else:
        port = 22
    data.scp_conns[ server_num ] = login(
        data.servers[server_num]['host'],
        data.servers[server_num]['user'],
        data.servers[server_num]['password'],
        port
        )



def printTotals(transferred, toBeTransferred):
    

    percent =(transferred / toBeTransferred ) *100

    progress =math.floor(  int(percent) /2  )
    if( percent >10 ):
        percent = "  %.2f" %percent
    else:
        percent = "   %.2f" %percent
    msg= "%s%% [%s>%s]%s  " %(percent,'=' * int(progress) ,' ' * int(50 - progress) ,group( transferred ) )
    sys.stdout.write( msg )
    sys.stdout.write( ('\b')  * len(msg))
    sys.stdout.flush()

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
