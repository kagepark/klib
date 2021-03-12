#Kage Park
import types
from sys import modules
from sys import version_info
if version_info[0] < 3:
    pass # Python 2 has built in reload
elif version_info[0] == 3 and version_info[1] <= 4:
    from imp import reload # Python 3.0 - 3.4 
else:
    from importlib import reload # Python 3.5+

# m=MODULE(globals())
# m.XXXX()
class MODULE:
    def __init__(self,globalv):
        self.src=globalv

    def Loaded(self,name):
        if type(name).__name__ == 'module':
            name=name.__name__
        if isinstance(name,str):
            if name in self.src:
                return True
        return False

    def Reload(self,name):
        if self.Loaded(name):
            if isinstance(name,str):
                modules[name]=reload(modules[name])
            else:
                name=reload(name)

    def Unload(self,name):
        if self.Loaded(name):
            if isinstance(name,str):
                del self.src[name]
                if name in modules:
                    del modules[name]
            elif isinstance(name,types.ModuleType):
                try:
                    nname = name.__spec__.name
                except AttributeError:
                    nname = name.__name__
                del self.src[nname]
                if nname in modules:
                    del modules[nname]

    #try:
    #    name = module.__spec__.name
    #except AttributeError:
    #    name = module.__name__
    # isinstance(module,types.ModuleType)
    def Import(self,*name):
        for a in name:
            #importlib.__import__(a)
            importlib.import_module(a)
