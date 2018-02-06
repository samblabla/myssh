try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
with open('requirements.txt') as f:
    required_packages = f.readlines()

setup(name='myssh',
    version='0.3.1',
    scripts=['script/myssh'],
    packages=['myssh'],
    author = "sam",  
    author_email = "yimingsha@qq.com",  
    install_requires=required_packages,
    )