from klib.kmisc import * # import kmisc(file)'s each function to local module's function
import os
import pickle
import types
import klib.TYPES as types
import sys

class GET:
    def __init__(self,src=None,**opts):
        self.src=src

    def __repr__(self):
        return repr(type(self.src).__name__)

    def Index(self,find,default=None,err=False):
        if isinstance(self.src,(list,tuple,str)):
            if find in self.src: return self.src.index(find)
        elif isinstance(self.src,dict):
            for i in self.src:
                if find == self.src[i]: return i
        if default == {'org'}:
            return self.src
        return default

    def Value(self,find,default=None,err=False):
        if isinstance(self.src,(list,tuple,str)):
            if isinstance(find,int):
                if len(self.src) > find:
                    return self.src[find]
        elif isinstance(self.src,dict):
            if find in self.src:
                return self.src[find]
        if default == {'org'}:
            return self.src
        return default

    def Read(self,default=False):
        if Is(self.src).Pickle():
            try:
                with open(self.src,'rb') as handle:
                    return pickle.load(handle)
            except:
                pass
        elif os.path.isfile(self.src):
            return file_rw(self.src)
        return default

    def Args(self,field='all',default={}):
        rt={}
        if isinstance(self.src,(types.ClassType,types.InstanceType)):
            try:
                self.src=getattr(self.src,'__init__')
            except:
                return self.src.__dict__
        elif not isinstance(self.src,types.FunctionType):
            return default
        args, varargs, keywords, defaults = inspect.getargspec(self.src)
        if defaults is not None:
            defaults=dict(zip(args[-len(defaults):], defaults))
            del args[-len(defaults):]
            rt['defaults']=defaults
        if args:
            rt['args']=args
        if varargs:
            rt['varargs']=varargs
        if keywords:
            rt['keywards']=keywords
        if isinstance(field,(list,tuple)):
            rts=[]
            for ii in field:
                rts.append(rt.get(ii,default))
            return rts
        else:
            if field in ['*','all']:
                return rt
            if field in rt:
                return rt[field]
        return default

    def FuncList(self):
        rt={}
        if isinstance(self.src,(types.ClassType,types.ModuleType)):
            for name,fobj in inspect.getmembers(self.src):
                if inspect.isfunction(fobj):
                    rt.update({name:fobj})
        return rt

    def FuncName(self,default=False,detail=False):
        #return traceback.extract_stack(None, 2)[0][2]
        try:
            dep=len(inspect.stack())-2
            if detail:
                return sys._getframe(dep).f_code.co_name,sys._getframe(dep).f_lineno,sys._getframe(dep).f_code.co_filename
            else:
                name=sys._getframe(dep).f_code.co_name
                if name == '_bootstrap_inner' or name == '_run_code':
                    return sys._getframe(3).f_code.co_name
                return name
        except:
            return default

    def ParentName(self):
        return traceback.extract_stack(None, 3)[0][2]

