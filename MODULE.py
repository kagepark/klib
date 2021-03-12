#Kage Park
import types
import inspect
from sys import modules
from sys import version_info
import importlib
import pip

if version_info[0] < 3:
    pass # Python 2 has built in reload
elif version_info[0] == 3 and version_info[1] <= 4:
    from imp import reload # Python 3.0 - 3.4 
else:
    from importlib import reload # Python 3.5+

class MODULE:
    def __init__(self):
        self.src=dict(inspect.getmembers(inspect.stack()[1][0]))["f_globals"] # Get my parent's globals()

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
            return True
        return False

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
    def Import(self,*inps,**opts):
        force=opts.get('force',None)
        for inp in inps:
            classm=False
            inp_a=inp.split()
            if inp_a[0] in ['from','import']:
                del inp_a[0]
            if 'as' in inp_a:
                name=inp_a[-1]
                module=inp_a[0]
            elif 'import' in inp_a:
                name=inp_a[-1]
                module=inp_a[0]
                classm=True
            elif len(inp_a) == 1:
                name=inp
                module=inp
            else:
                return
            if force:
                if self.Reload(name):
                    continue
            try:
                if classm:
                    self.src[name]=getattr(importlib.import_module(module),name)
                else:
                    self.src[name]=importlib.import_module(module)
            except ImportError:
                if hasattr(pip,'main'):
                    pip.main(['install',module])
                else:
                    pip._internal.main(['install',module])
            finally:
                if classm:
                    self.src[name]=getattr(importlib.import_module(module),name)
                else:
                    self.src[name]=importlib.import_module(module)

    def Load(self,*inps,**opts):
        self.Import(*inps,**opts)

    def List(self):
        return list(self.src.keys())

    def Dict(self):
        return self.src
