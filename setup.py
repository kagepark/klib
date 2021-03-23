#Kage Park
import os
import setuptools
from klib.MODULE import *
MODULE().Import('klib.SHELL import SHELL')

def lib_ver():
    gver=SHELL().Run('''git describe --tags | sed "s/^v//g" | sed "s/^V//g"''')
    if gver[0] == 0:
        return gver[1]
    return '2.0'

long_description=''
if os.path.isfile('README.md'):
    with open("README.md", "r") as fh:
        long_description = fh.read()

setuptools.setup(
    name='klib',
    version='{}'.format(lib_ver()),
#    scripts=['klib'],
    author='Kage Park',
    #autor_email='',
    description='Enginering useful library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kagepark/klib",
    packages=setuptools.find_packages(),
    classifiers=[
#        "Programming Language :: Python :: 2",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
)
