#Kage Park
import random
import re
from klib.MODULE import *
MODULE().Import('from klib.CONVERT import CONVERT')

class STR(str):
    def __init__(self,src):
        self.src=src

    def Rand(self,length=8,strs=None,mode='*'):
        if not isinstance(strs,str):
            if mode in ['all','*','alphanumchar']:
                strs='0aA-1b+2Bc=C3d_D,4.eE?5"fF6g7G!h8H@i9#Ij$JkK%lLmMn^N&oO*p(Pq)Q/r\Rs:St;TuUv{V<wW}x[Xy>Y]z|Z'
            elif mode in ['alphanum']:
                strs='aA1b2BcC3dD4eE5fF6g7Gh8Hi9IjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
            else:
                strs='aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'
        new=''
        strn=len(strs)-1
        for i in range(0,length):
            new='{0}{1}'.format(new,strs[random.randint(0,strn)])
        return new

    def Cut(self,head_len=None,body_len=None):
        if not isinstance(self.src,str):
           self.src='''{}'''.format(self.src)
        str_len=len(self.src)

        if not head_len or head_len >= str_len:
           return [self.src]

        if not body_len:
            return [self.src[i:i + head_len] for i in range(0, str_len, head_len)]
        rt=[]
        rt.append(self.src[0:head_len]) # Take head
        # Cut body
        string_tmp=self.src[head_len:]
        string_tmp_len=len(string_tmp)
        for i in range(0, int(string_tmp_len/body_len)+1):
            if (i+1)*body_len > string_tmp_len:
               rt.append(string_tmp[body_len*i:])
            else:
               rt.append(string_tmp[body_len*i:(i+1)*body_len])
        return rt

    def Tap(self,space='',sym='\n',default=None,NFLT=False):
        # No First Line Tap (NFLT)
        if isinstance(space,int):
            sspace=''
            for i in range(0,space):
                sspace='{}{}'.format(sspace,' ')
            space=sspace
        if isinstance(self.src,str):
            self.src=self.src.split(sym)
        if isinstance(self.src,(list,tuple)):
            rt_str=''
            if NFLT:
                rt_str='%s'%(self.src.pop(0))
            for ii in self.src:
                if rt_str:
                    rt_str='%s%s%s%s'%(rt_str,sym,space,ii)
                else:
                    rt_str='%s%s'%(space,ii)
            return rt_str
        return default

    def Reduce(self,start=0,end=None,sym=None,default=None):
        if isinstance(self.src,str):
            if sym:
                arr=self.src.split(sym)
                if isinstance(end,int):
                    return sym.join(arr[start:end])
                else:
                    return sym.join(arr[start])
            else:
                if isinstance(end,int):
                    return self.src[start:end]
                else:
                    return self.src[start:]
        return default

    def Find(self,find,prs=None,sym='\n',patern=True):
        # Patern return selection (^: First(0), $: End(-1), <int>: found item index)
        found=[]
        if not isinstance(self.src,str): return found
        if sym:
            string_a=self.src.split(sym)
        else:
            string_a=[self.src]
        for nn in string_a:
            if not isinstance(find,(list,tuple)):
                find=[find]
            for ff in find:
                if patern:
                    aa=re.compile(ff).findall(nn)
                    for mm in aa:
                        if type(mm) is tuple:
                            if prs == '^':
                                found.append(mm[0])
                            elif prs == '$':
                                found.append(mm[-1])
                            elif type(prs) is int:
                                found.append(mm[prs])
                            else:
                                found.append(mm)
                        else:
                            found.append(mm)
                else:
                    find_a=ff.split('*')
                    if len(find_a[0]) > 0:
                        if find_a[0] != nn[:len(find_a[0])]:
                            chk=False
                    if len(find_a[-1]) > 0:
                        if find_a[-1] != nn[-len(find_a[-1]):]:
                            chk=False
                    for ii in find_a[1:-1]:
                        if ii not in nn:
                            chk=False
                    if chk:
                        found.append(nn)
        return found

    def Int(self,encode='utf-8'):
        if Py3:
            if isinstance(self.src,bytes):
                return int(self.src.hex(),16)
            else:
                return int(CONVERT(self.src).Bytes(encode=encode).hex(),16)
        return int(self.src.encode('hex'),16)

    def Replace(self,replace_what,replace_to,default=None):
        if isinstance(self.src,str):
            if replace_what[-1] == '$' or replace_what[0] == '^':
                return re.sub(replace_what, replace_to, self.src)
            else:
                head, _sep, tail = self.src.rpartition(replace_what)
                return head + replace_to + tail
        return default

    def Url(self):
        if isinstance(self.src,str):
            return self.src.replace('+','%2B').replace('?','%3F').replace('/','%2F').replace(':','%3A').replace('=','%3D').replace(' ','+')
        return self.src

    def Split(self,sym=None):
        if isinstance(self.src,str):
            try:
                return re.split(sym,self.src)
            except:
                return self.src.split(sym)
#            if isinstance(sym,str) and '|' in sym: # splited by '|' for each characters
#                return re.split(sym,self.src)
#            else: # Single character
#                return self.src.split(sym)
