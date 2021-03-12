#Kage Park
from klib.kmisc import *
from klib.IS import IS
import ast

class CONVERT:
    def __init__(self,src):
        self.src=src

    def Int(self,default=False):
        if isinstance(self.src,int): return self.src
        try:
            return int(self.src)
        except:
            return default

    def Str2int(self,encode='utf-8'):
        if IS().py3():
            if isinstance(self.src,bytes):
                return int(self.src.hex(),16)
            else:
                return int(self.bytes(encode=encode).hex(),16)
        return int(self.src.encode('hex'),16)

    def Bytes(self,encode='utf-8'):
        if IS().py3():
            if isinstance(self.src,bytes):
                return self.src
            else:
                return bytes(self.src,encode)
        return bytes(self.src) # if change to decode then network packet broken

    def Str(self,encode='latin1'): # or windows-1252
        #type_val=type(val)
        #if IS().py3() and type_val is bytes:
        if IS().py3() and isinstance(self.src,bytes):
            return self.src.decode(encode)
        #elif type_val.__name__ == 'unicode':
        elif isinstance(self.src,unicode):
            return self.src.encode(encode)
        return '''{}'''.format(self.src)

    def Ast(self,default=False):
        if isinstance(self.src,str):
            try:
                ast.literal_eval(string)
            except:
                return default
        else:
            return self.src

    def Form(self,default=False):
        return self.Ast(default=default)
