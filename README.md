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

# Bmc handle Class
Added SMCIPMITool.jar command information
Default is IPMITOOL command
Require kDict and kmisc module

## Contents
1. Added New commands
   1. bmc_cmd() : command converter between SMCIPMITool and IPMITOOL
   1. find_user_pass() : Find BMC Password and User name from defined lists
   1. recover_user_pass() : Recover BMC User/Password to original defined 
   1. reset() : Reset BMC
   1. get_mac() : Get BMC Mac address
   1. get_eth_mac() : Get Ethernet Mac address
   1. ping(): ping to BMC IP
   1. info(): Print BMC Information
   1. is_up() : Node is UP?
   1. is_down() : Node is Down?
   1. power_handle() : Node power handle

Example)
```javascript
root=kDict.kDict()
def log(msg,**opts):
    log_level=opts.get('log_level',8)
    direct=opts.get('direct',False)
    import sys
    if log_level < 6:
        if direct:
            sys.stdout.write(msg)
        else:
            sys.stdout.write(msg+'\n')
        sys.stdout.flush()
bmc=kBmc.kBMC(root,'192.168.1.100',ipmi_user='ADMIN',ipmi_pass='ADMIN',tool_path='/usr/local/bin',log=log)
print(bmc.info())
print(bmc.power_handle('status'))
print(bmc.power_handle('off_on'))
print(bmc.power_handle('status'))
print(bmc.power_handle('off',verify=False))
print(bmc.power_handle('status'))
```

# MISC functions
Useful commands
