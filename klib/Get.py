#Kage Park
from klib.Abs import *

def Get(*inps,**opts):
    default=opts.get('default',None)
    out=opts.get('out',None)
    err=opts.get('err',True)
    check=opts.get('check',(str,list,tuple,dict))
    key=None
    if len(inps) >= 2:
        src=inps[0]
        key=inps[1:]
    elif len(inps) == 1:
        src=inps[0]
        key=opts.get('key',None)
        if isinstance(key,list):
            key=tuple(key)
        elif key is not None:
            key=(key,)
    rc=[]
    src_name=type(src).__name__
    if key is None:
        # Get Class/instance's Function list or variable list
        if src_name in ['kDict','kList']: return src.Get()
        if src_name in ['instance','classobj']:
            def method_in_class(class_name):
                ret=dir(class_name)
                if hasattr(class_name,'__bases__'):
                    for base in class_name.__bases__:
                        ret=ret+method_in_class(base)
                return ret
            return method_in_class(src)
        # if not class/instance then return error
        if err in [True,'err','True']:
            return OutFormat(default,out=out)
        return OutFormat(src,out=out)
    if isinstance(src,tuple(check)):
        if isinstance(src,(str,list,tuple)) and len(src)>0:
            if src_name in ['kList']: src=src.Get()
            #Get data in the list's index
            for kk in Abs(*key,obj=src,out=list,default=[None],err=False):
                if kk is None:
                    if err != 'ignore':rc.append(default)
                else:
                    rc.append(src[kk])
            if not rc and err in [True,'err','True']:return OutFormat(default,out=out)
            return OutFormat(rc,out=out)
        elif isinstance(src,dict) and len(src) > 0:
            if src_name in ['kDict']: src=src.Get()
            #Get data in the dictionary's key
            nkeys=Abs(*key,obj=src,out=list,default=[None],err=False)
            if nkeys:
                for kk in Abs(*key,obj=src,out=list,default=[None],err=False):
                    rr=src.get(kk,default)
                    if rr == default:
                        if err != 'ignore':rc.append(rr)
                    else:
                        rc.append(rr)
                if not rc and err in [True,'err','True']:return OutFormat(default,out=out)
                return OutFormat(rc,out=out)
            return src.get(key[0],default)
    elif type(src).__name__ in ['instance','classobj']:
        # get function object of finding string name in the class/instance
        if isinstance(key,(list,tuple,dict)):
            for kk in key:
                rc.append(getattr(src,kk,default))
            if not rc and err in [True,'err','True']:return OutFormat(default,out=out)
            return OutFormat(rc,out=out)
        return getattr(src,key,default)
    if err in [True,'err','True']:return OutFormat(default,out=out)
    return OutFormat(src,out=out)


