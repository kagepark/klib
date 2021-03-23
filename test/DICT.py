import os
import sys
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-2])+'/klib')
from klib.MODULE import *
MODULE().Import('klib.DICT import DICT')

test={
      'a':123,
      'b':{
         'c':{'ddd'},
         'e':{},
         'z':123,
      }
    }
root=DICT(test)
print('** base:')
root.Print()

print('** Add tree/apple:')
root.Mk('tree.apple')
root.Print()
print('** tree/apple/color = red')
root.tree.apple.color='red'
print('** get tree/apple/color:',root.tree.apple.color.Get())
print('** put white-red to tree/apple/color')
root.tree.apple.Put('color','white-red')
print('** get tree/apple/color:',root.tree.apple.color.Get())
print('** put white at monkey in tree/yellow with create new yellow path')
root.tree.Put('monkey','white',path='yellow')
print('** get tree/yellow/monkey:',root.tree.yellow.monkey.Get())
print('** put black at monkey in tree/yellow with new=True option for update data when new case only')
rc=root.tree.Put('monkey','black',new=True,path='yellow')
print('** get tree/yellow/monkey:',root.tree.yellow.monkey.Get(),rc)
print('** put black at monkey in tree/yellow for update data')
rc=root.tree.Put('monkey','black',path='yellow')
print('** get tree/yellow/monkey:',root.tree.yellow.monkey.Get(),rc)
root.tree.Put('color','yellow',path='banana')
print(root.tree.banana)
print('** add banana2')
root.tree.banana.Put('banana2','white')
print(root.tree.banana.Get())
#print('** change color white to yellow at banana2')
#root.tree.banana.Put('banana2','yellow')
#print(root.tree.banana.Get())
print('** set readonly')
root.tree.banana.color.Proper('readonly',True)
#print(root.tree.banana.Get())
#print('** put at readonly')
#root.tree.banana.Put('color','black')
#print(root.tree.banana.Get())
#print('** force put banana-color  yellow to black2')
#root.tree.banana.Put('color','black2',force=True)
#print(root.tree.banana.Get())
#print('** del at readonly')
#root.tree.banana.Del('color')
#print(root.tree.banana.Get())
#print('** del at readonly with force')
#root.tree.banana.Del('color',force=True)
#print(root.tree.banana.Get())
#print('** pop at readonly')
#aa=root.tree.banana.POP('color')
#print(aa,root.tree.banana.Get())
#print('** pop at readonly with force')
#aa=root.tree.banana.POP('color',force=True)
#print(aa,root.tree.banana.Get())
########
print('** update at readonly to uuuu')
root.tree.banana.Update({'color':'uuuu'})
print(root.tree.banana.Get())
print('** force update banana-color  yellow to uuuu2')
root.tree.banana.Update({'color':'uuuu2'},force=True)
print(root.tree.banana.Get())
print('-------------------------')
##############

root.tree.apple['color']='red'
root.tree.apple.color.Get()
root.tree.apple.Get('color')
root.tree.apple.color.Proper('readonly',True)
root.tree.apple.Put('color','white')
root.tree.apple.color.Proper('readonly',False)
root.tree.apple.Put('color','white')
root.Print()
print(root.Find('readonly',proper=True))
print(root.Find('apple',mode='key'))
print(root.Find('white'))
print(root.Find(123))
print(root.Find('yellow',mode='*'))
