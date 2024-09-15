import sys
import importlib.metadata

# 确保至少需要 Python 3.6
if sys.version_info < (3, 6):
    print('At least Python 3.6 is required')
    sys.exit(1)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# 读取 requirements.txt 文件
with open('requirements.txt', encoding='utf-8') as f:
    required_packages = [line.strip() for line in f if not line.strip().startswith('#')]


from myssh import config
setup(
    name='myssh',
    version=config.version,
    scripts=['script/myssh'],
    packages=['myssh'],
    author="sam",
    author_email="yimingsha@qq.com",
    install_requires=required_packages,
    entry_points={
        'console_scripts': [
            'myssh = myssh.myssh:main',
        ],
    },
)