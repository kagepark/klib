#Kage Park
import ast
import struct
from klib.MODULE import MODULE
MODULE().Import('from klib.Type import Type')
MODULE().Import('from klib.kmisc import *')
MODULE().Import('from klib.IS import IS')

class CONVERT:
    def __init__(self,src):
        self.src=src

#    def Int(self,encode='utf-8'):
#        if IS().Py3():
#            if isinstance(self.src,bytes):
#                return int(self.src.hex(),16)
#            else:
#                return int(CONVERT(self.src).Bytes(encode=encode).hex(),16)
#        return int(self.src.encode('hex'),16)

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

    def Mac2Str(self,case='lower',default=False):
        if IS(self.src).Mac4():
            if case == 'lower':
                self.src=self.src.strip().replace(':','').replace('-','').lower()
            else:
                self.src=self.src.strip().replace(':','').replace('-','').upper()
            return self.src
        return default

    def Str2Mac(self,case='lower',default=False,sym=':',chk=False):
        if isinstance(self.src, str):
            self.src=self.src.strip()
            if len(self.src) in [12,17]:
                self.src=self.src.replace(':','').replace('-','')
                if len(self.src) == 12:
                    self.src=sym.join(self.src[i:i+2] for i in range(0,12,2))
                if case == 'lower':
                    self.src=self.src.lower()
                else:
                    self.src=self.src.upper()
        if chk:
            if not IS(self.src).Mac4():
                return  default
        return self.src

    def Size(self,unit='b:g',default=False):
        if not isinstance(self.src,int):
            return default
        unit_a=unit.lower().split(':')
        if len(unit_a) != 2:
            return False
        def inc(sz):
            return '%.1f'%(float(sz) / 1024)
        def dec(sz):
            return int(sz) * 1024
        sunit=unit_a[0]
        eunit=unit_a[1]
        unit_m=['b','k','m','g','t','p']
        si=unit_m.index(sunit)
        ei=unit_m.index(eunit)
        h=ei-si
        for i in range(0,abs(h)):
            if h > 0:
                self.src=inc(self.src)
            else:
                self.src=dec(self.src)
        return self.src

