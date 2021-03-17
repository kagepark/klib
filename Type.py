#Kage Park
"""
Based on Python2.7 and Python3.x's types module
Inhance for make sure
"""
import sys
from klib.MODULE import MODULE
MODULE().Import('filetype')

def Type(*inp,**opts):
    inpn=len(inp)
    default=opts.get('default',None)
    if inpn == 0: return default
    obj=inp[0]
    if inpn == 1:
        if isinstance(obj,str) and os.path.isfile(obj):
            aa=filetype.guess(obj)
            if aa: return aa.__dict__.get('_Type__extension') # File Type
            try:
                with open(obj,'rb') as f: # Pickle Type
                    pickle.load(f)
                    return 'pickle'
            except:
                pass
        else:
            obj_dir=dir(obj)
            obj_name=type(obj).__name__
            if '__dict__' in obj_dir:
                if obj_name == 'type': return 'classobj'
                return 'instance'
            if obj_name == 'type':return obj.__name__ # type's name
            return obj_name # Object Name
    else:
        chk_type=[]
        for name in inp:
            if isinstance(name,(list,tuple)):
                for  ii in name:
                    if ii == 'instance':
                        if '__dict__' in dir(obj) and type(obj) is not type: return True
                    else:
                        a=ConvertType(ii)
                        if a is True:  return True
                        if a is not None: chk_type.append(a)
            else:
                if name == 'instance':
                    if '__dict__' in dir(obj) and type(obj) is not type:  return True
                else:
                    a=ConvertType(name)
                    if a is True: return True
                    if a is not None: chk_type.append(a)
        if chk_type:return isinstance(obj,tuple(chk_type))
        return False

def ConvertType(ii):
   if ii is None:
       return type(None)
   elif isinstance(ii,type):
       return ii
   elif isinstance(ii,str):
       if sys.version_info[0] >= 3:
           if ii == 'long': return int # py3 not support LONG. INT support long range
           if ii == 'unicode': return bytes
       if ii in ['function','code','getset_descriptor','member_descriptor','func','def']:
           def _A(): pass
           if ii in ['function','func','def']:
               return type(_A)
           elif ii == 'getset_descriptor':
               if sys.version_info[0] < 3: return type(type(_A).func_code)
               return type(type(_A).__code__)
           elif ii == 'member_descriptor':
               if sys.version_info[0] < 3: return type(type(_A).func_global)
               return type(type(_A).__globals__)
           else:
               if sys.version_info[0] < 3:
                   return type(_A.func_code)
               else:
                   return type(_A.__code__)
           del _A
       elif ii == 'lambda':
           return type(lambda: None)
       elif ii == 'module':
           return type(sys)
       elif ii in ['classobj','class','instance','instancemethod']:
           class _C:
               def _m(self): pass
           if ii in ['classobj','class']:return type(_C)
           if ii == 'instance': return type(_C())
           if ii == 'instancemethod': return type(_C()._m)
       elif ii in ['builtin_function_or_method','builtin']:
           return type(len)
       elif ii in ['dictproxy']:
           return type(int.__dict__)
       elif ii in ['NotImplementedType']:
           return type(NotImplemented)
       try:
           return eval(ii)
       except:
           return None
