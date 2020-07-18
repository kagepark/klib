# Custom Dictionary Class

Convert Dictionary to Object style Dictionary

- Initialize dictionary 


> test={
>      'a':123,
>      'b':{
>         'c':{'ddd'},
>         'e':{}
>      }
>     }
>
> root=kDict(test)

or 

’’’>> root=kDict()’’’

- Add new data
> root.tree.apple.color='red'

or

> root.tree.apple.PUT('color','red')

or

> root.tree.apple['color']='red'

- Get data
> root.tree.apple.color.GET()

or

> root.tree.apple.GET('color')

- Print dictionary
> root.PRINT()

> root.tree.PRINT()

- Set property at Apple's color

  I. Set readonly
> root.tree.apple.color.PROPER('readonly',True)

  I. Try change data
> root.tree.apple.PUT('color','white')

item is readonly

>root.tree.PRINT()

{'color': {'._d': 'red', '._p': {'readonly': True}}}

  I. Unset readonly
> root.tree.apple.color.PROPER('readonly',False)

  + Try change data
> root.tree.apple.PUT('color','white')
> root.tree.PRINT()

{'color': {'._d': 'red', '._p': {'readonly': True}}}
