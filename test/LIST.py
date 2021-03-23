import os
import sys
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-2])+'/klib')
from klib.MODULE import *
MODULE().Import('klib.LIST import LIST')

l=LIST(1)
print(l,type(l))
l.Append(2)
print('l:',l)
print(tuple(l.Get()))
l.Get().append(3)
print(l)
print(l.Get(-1))
print(l.Get(-9))
l.Insert('I','I2',at=2)
print(l)
l.Insert('E','E2',at=-0)
print(l)
l.Append('A','A2')
print(l)
