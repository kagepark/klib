# Custom Dictionary Class

Convert Dictionary to Object style Dictionary
## Contents
1. Create tree type items 
1. Added New commands
   1. PUT()    : Put value at a item
   1. GET()    : Get value of item
   1. DEL()    : Delete item
   1. UPDATE() : Update value at item
   1. PRINT()  : Print dictionary 
   1. DIFF()   : Compare two dictionary
   1. CHECK()  : Check put the value is same as the item(key)'s value
   1. LIST()   : Return list of keys value 
   1. PROPER() : Show/Set/Update property at the item.
1. Added property at each key

- Initialize dictionary 


```javascript
>>> test={
      'a':123,
      'b':{
         'c':{'ddd'},
         'e':{}
      }
    }
root=kDict(test)
```

or 

```javascript
>>> root=kDict()
```

- Add new data

```javascript
>>> root.tree.apple.color='red'
```
or

```javascript
>>> root.tree.apple.PUT('color','red')
```
or
```javascript
>>> root.tree.apple['color']='red'
```
- Get data
```javascript
>>> root.tree.apple.color.GET()
```
or
```javascript
>>> root.tree.apple.GET('color')
```
- Print dictionary
```javascript
>>> root.PRINT()
>>> root.tree.PRINT()
```
- Set property at Apple's color

  - Set readonly
```javascript
>>> root.tree.apple.color.PROPER('readonly',True)
```
  - Try change data
```javascript
>>> root.tree.apple.PUT('color','white')
item is readonly

>>> root.tree.PRINT()
{'color': {'._d': 'red', '._p': {'readonly': True}}}
```
  - Unset readonly
```javascript
>>> root.tree.apple.color.PROPER('readonly',False)
```
  - Try change data
```javascript
>>> root.tree.apple.PUT('color','white')
>>> root.tree.PRINT()
{'color': {'._d': 'red', '._p': {'readonly': True}}}
```
