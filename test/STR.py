import os
import sys
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-2])+'/klib')
from klib.MODULE import *
MODULE().Import('klib.STR import STR')

aa='''App.py:from distutils.spawn import find_executabledeg
IPMICfg.py:from distutils.spawn import find_executable
kBmc.py:from distutils.spawn X11 import find_executable
kBmc.py:from disTutils. spawn X11abc import find_executable
kBmc.py:        if find_executable('ipmitool') is False:
kmisc.py:from distutils.spawn X113 import from find_executable
kmisc.py:        if find_executable('ping'):
kmisc.py:           if find_executable('ping'):
misc.py adf widk lsu 
Nutanix.py:from distutils.spawn X121 import find_executable
SMCIPMITool.py:from dist X12iTU utils.spawn import find_executable
SumEFI.py:from distutils.spawn import find_executable
Sum.py:from distutils.spawn import find_executable'''

print(STR(aa).Find('(\w*exec*)',findall=True))
print(STR(aa).Index('from'))
print(STR(aa).Index('from',findall=True))
print(STR(aa).Find('from (\w*).spawn',pattern=True,findall=True))
print(STR(aa).Index('from (\w*).spawn',pattern=True))
print(STR(aa).Find('from (\w*).spawn',pattern=True))
print(STR(aa).Index('from (\w*).spawn',pattern=True,findall=True))

print(STR(aa).Find('X(\d*)[a-zA-Z]',findall=True))
print(STR(aa).Index('(X11)[ a-zA-Z]',findall=True))
print(STR(aa).Find('(X11)[ a-zA-Z]',findall=True))
print(STR(aa).Find('(X31)[ a-zA-Z]',findall=True))
print(STR(aa).Index('^misc.py',findall=True))
print(STR(aa).Index('find_executabledeg$',findall=True))
print(STR(aa).Split('\n|:'))

print(STR(aa).Tap(space='    ',NFLT=True,out=list))
print(STR(aa).Tap(space='    ',NFLT=True))
print(STR(aa).Cut(55))
