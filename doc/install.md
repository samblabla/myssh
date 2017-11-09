# 安装

1. 解压 require.tar.gz

2. 进入 Pycrypto目录、Paramiko目录 和 PyYAML目录,用以下命令安装python模块(或者使用pip进行模块安装)
> python 安装步骤:
> 
```
python setup.py build
python setup.py install
```

3. 进入 sshpass 目录
>
```
./configure
make &&make install
```

4. 在 ~/.bash_profile里加入:

```
 alias myssh="python /文件所在的路径/myssh.py"
``` 

在命令行中使用 myssh 打开工具


>
如果运行myssh时出现这个错误 UnicodeEncodeError: 'ascii' codec can't encode characters
>
在~/.bash_profile中添加
export PYTHONIOENCODING=UTF-8
