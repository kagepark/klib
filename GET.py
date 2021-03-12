from klib.kmisc import * # import kmisc(file)'s each function to local module's function
import os
import pickle

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
