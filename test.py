import kDict
test={
      'a':123,
      'b':{
         'c':{'ddd'},
         'e':{},
         'z':123,
      }
    }
root=kDict.kDict(test)
root.tree.apple.color='red'
root.tree.apple.PUT('color','red')
root.tree.yellow.PUT('monkey','white')
root.tree.banana.PUT('color','yellow')
print(root.tree.banana)
#print('** add banana2')
#root.tree.banana.PUT('banana2','white')
#print(root.tree.banana.GET())
#print('** change color white to yellow at banana2')
#root.tree.banana.PUT('banana2','yellow')
#print(root.tree.banana.GET())
print('** set readonly')
root.tree.banana.color.PROPER('readonly',True)
#print(root.tree.banana.GET())
#print('** put at readonly')
#root.tree.banana.PUT('color','black')
#print(root.tree.banana.GET())
#print('** force put banana-color  yellow to black2')
#root.tree.banana.PUT('color','black2',force=True)
#print(root.tree.banana.GET())
#print('** del at readonly')
#root.tree.banana.DEL('color')
#print(root.tree.banana.GET())
#print('** del at readonly with force')
#root.tree.banana.DEL('color',force=True)
#print(root.tree.banana.GET())
#print('** pop at readonly')
#aa=root.tree.banana.POP('color')
#print(aa,root.tree.banana.GET())
#print('** pop at readonly with force')
#aa=root.tree.banana.POP('color',force=True)
#print(aa,root.tree.banana.GET())
########
print('** update at readonly to uuuu')
root.tree.banana.UPDATE({'color':'uuuu'})
print(root.tree.banana.GET())
print('** force update banana-color  yellow to uuuu2')
root.tree.banana.UPDATE({'color':'uuuu2'},force=True)
print(root.tree.banana.GET())
print('-------------------------')
##############

root.tree.apple['color']='red'
root.tree.apple.color.GET()
root.tree.apple.GET('color')
root.tree.apple.color.PROPER('readonly',True)
root.tree.apple.PUT('color','white')
root.tree.apple.color.PROPER('readonly',False)
root.tree.apple.PUT('color','white')
root.PRINT()
print(root.FIND('readonly',proper=True))
print(root.FIND('apple',mode='key'))
print(root.FIND('white'))
print(root.FIND(123))
print(root.FIND('yellow',mode='*'))
