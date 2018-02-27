import sys
if sys.version_info < (2,7):
    print('At least Python 2.7 is required')
    exit()

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
with open('requirements.txt') as f:
    required_packages = f.readlines()
    
from myssh import config
setup(name='myssh',
    version=config.version,
    scripts=['script/myssh'],
    packages=['myssh'],
    author = "sam",  
    author_email = "yimingsha@qq.com",  
    install_requires=required_packages,
    )