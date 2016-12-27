# 安装

1. 解压 require.zip

2. 进入 Paramiko目录 和 PyYAML目录 用以下命令安装pyton模块
> python 安装步骤:
> 
```
python setup.py build
python setup.py install
```

3. 进入 sshpass 目录

```
./configure
make &&make install
```

4. 在 ~/.bash_profile是加入:

```
 alias myssh="python /文件所在的路径/myssh.py"
``` 

在命令行中使用 myssh 打开工具

