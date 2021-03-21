#Kage Park
"""
Based on Python2.7 and Python3.x's types module
Inhance for make sure
"""
import sys,os
from klib.MODULE import *
#MODULE().Import('filetype')
MODULE().Import('magic')

def TypeName(obj,default=None):
    if isinstance(obj,str):
        if os.path.isfile(obj):
            #aa=filetype.guess(obj)
            #if aa: return aa.__dict__.get('_Type__extension') # File Type
            aa=magic.from_buffer(open(obj,'rb').read(2048))
            if aa: return aa.split()[0].lower()
            try:
                with open(obj,'rb') as f: # Pickle Type
                    pickle.load(f)
                    return 'pickle'
            except:
                pass
        else:
            return obj.lower()
    else:
        obj_dir=dir(obj)
        obj_name=type(obj).__name__
        if obj_name in ['function']: return obj_name
        if '__dict__' in obj_dir:
            if obj_name == 'type': return 'classobj'
            return 'instance'
        elif obj_name == 'type':
            return obj.__name__
        return obj_name.lower() # Object Name
    return default

def TypeFixer(name,default=None):
    if name == default: return default
    obj=name.lower()
    if obj in ['none']: return 'nonetype'
    if obj in ['obj']: return 'object'
    if obj in ['long']:
        if sys.version_info[0] < 3: return obj
        return 'int'
    if obj in ['class']: return 'classobj'
    if obj in ['builtinfunction','builtinmethod','builtin_function_or_method']: return 'builtin_function_or_method'
    # function: function and instance's function in Python3
    # method:  class's function in Python3
    # instancemethod: instance's and class's function in Python2
    if obj in ['method','classfunction','instancemethod','unboundmethod']: return 'method' # function in the class
    if obj in ['dictproxy','mappingproxy']: return ['dictproxy','mappingproxy'] # function in the class
    return name

def Type(*inp,**opts):
    '''
       instance: <class name>()
       classobj : <class name>
       function : <func name>
       return value: <func name>()
       method   : <class name>().<func name>
    '''
    inpn=len(inp)
    default=opts.get('default',None)
    if inpn == 0: return default
    obj=inp[0]
    if inpn == 1: return TypeName(obj,default=default)
    chk_type=[]
    for name in inp[1:]:
        if not isinstance(name,(tuple,list)): name=[name]
        for ii in name:
            a=TypeFixer(TypeName(ii,default=default),default=default)
            if a == default: continue
            if isinstance(a,list): 
                chk_type=chk_type+a
            elif a not in chk_type:
                chk_type.append(a)
    if chk_type: 
        obj_type=TypeName(obj)
        if obj_type == default: return default
        if obj_type == 'instance':
            if 'int' in chk_type: 
                if isinstance(obj,int): return True
            elif 'dict' in chk_type:
                if isinstance(obj,dict): return True
            elif 'list' in chk_type:
                if isinstance(obj,list): return True
            elif 'tuple' in chk_type:
                if isinstance(obj,tuple): return True
            elif 'float' in chk_type:
                if isinstance(obj,float): return True
        if obj_type in chk_type: return True
    return False

if __name__ == "__main__":
    print('None:',TypeName(None),type(None))
    print('type:',TypeName(type),type(type))
    print('object:',TypeName(object),type(object))
    print('int:',TypeName(int),type(int))
    if sys.version_info[0] < 3:
        print('long:',TypeName(long),type(long))
    print('float:',TypeName(float),type(float))
    print('bool:',TypeName(bool),type(bool))
    print('str:',TypeName(str),type(str))
    if sys.version_info[0] < 3:
        print('unicode:',TypeName(unicode),type(unicode))
    print('bytes:',TypeName(bytes),type(bytes))
    print('tuple:',TypeName(tuple),type(tuple))
    print('list:',TypeName(list),type(list))
    print('dict:',TypeName(dict),type(dict))
    def _F(): pass
    print('function:',TypeName(_F),type(_F))
    print('lambda:',TypeName(lambda: None),type(lambda: None))

    if sys.version_info[0] < 3:
        print('code v2:',TypeName(_F.func_code),type(_F.func_code)) #v2
    else:
        print('code v3:',TypeName(_F.__code__),type(_F.__code__)) #v3
    def _Y(): 
        yield 1
    print('generator(yield):',TypeName(_Y()),type(_Y()))
    class _C:   # basic class
        def _M(self): pass
    print('**class:',TypeName(_C),type(_C))
    print('**class ?:',Type(_C,dict))
    print('instance:',TypeName(_C()),type(_C()))
    print('instance ?:',Type(_C(),dict))
    print('unboundMethod:',TypeName(_C._M),type(_C._M))
    print('method:',TypeName(_C()._M),type(_C()._M))
    class _D(dict): # inheritance class
        def _H(self): pass
    print('**class-dict:',TypeName(_D),type(_D))
    print('**class-dict True:',Type(_D,dict))
    print('**class-dict False:',Type(_D,int))
    print('instance:',TypeName(_D()),type(_D()))
    print('instance-dict True:',Type(_D(),_D()))
    print('instance-dict False:',Type(_D(),_D))
    print('instance-dict True:',Type(_D(),dict))
    print('instance-dict True2:',Type(_D(),('abc','dic',dict)))
    print('instance-dict True3:',Type(_D(),'abc','Dict'))
    print('instance-dict False:',Type(_D(),int))
    print('unboundMethod:',TypeName(_D._H),type(_D._H))
    print('method:',TypeName(_D()._H),type(_D()._H))

    print('builtinfunction:',TypeName(len),type(len))
    print('builtinmethod:',TypeName([].append),type([].append))

    print('module:',TypeName(os),type(os))
    print('slice:',TypeName(slice),type(slice))
    print('ellipsis:',TypeName(Ellipsis),type(Ellipsis))
    print('dictproxy:',TypeName(type.__dict__),type(type.__dict__))
    print('notimplemented:',TypeName(NotImplemented),type(NotImplemented))

    if sys.version_info[0] < 3:
        print('getsetdescriptor v2:',TypeName(_F.func_code),type(_F.func_code))
        print('memberdescriptor v2:',TypeName(_F.func_globals),type(_F.func_globals))
    else:
        print('getsetdescriptor v3:',TypeName(_F.__code__),type(_F.__code__))
        print('memberdescriptor v3:',TypeName(_F.__globals__),type(_F.__globals__))

