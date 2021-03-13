#Kage Park
class STR(str):
    def __init__(self,src):
        self.src=src

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

    def Tap(self,space='',sym='\n',default=None):
        if isinstance(space,int):
            sspace=''
            for i in range(0,space):
                sspace='{}{}'.format(sspace,' ')
            space=sspace
        if isinstance(self.src,str):
            self.src=self.src.split(sym)
        if isinstance(self.src,(list,tuple)):
            rt_str=''
            for ii in self.src:
                if NFLT:
                    rt_str='%s'%(ii)
                    NFLT=False
                else:
                    if rt_str:
                        rt_str='%s%s%s%s'%(rt_str,sym,space,ii)
                    else:
                        rt_str='%s%s'%(space,ii)
            return rt_str
        return default
