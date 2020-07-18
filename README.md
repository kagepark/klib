# Custom Dictionary Class

Convert Dictionary to Object style Dictionary

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
