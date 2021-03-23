# Kage Park
from klib.MODULE import *

class CRC:
    def __init__(self,**opts):
        self.rtd=opts.get('rc',{'GOOD':[True,'True','Good','Ok','Pass',{'OK'},0],'FAIL':[False,'False','Fail',{'FAL'}],'NONE':[None,'None','N/A',{'NA'}],'IGNO':['IGNO','Ignore',{'IGN'}],'ERRO':['ERR','Error',{'ERR'}],'WARN':['Warn',{'WAR'}],'UNKN':['Unknown','UNKN',{'UNK'}],'JUMP':['Jump',{'JUMP'}]})

    def Trans(self,irt):
        type_irt=type(irt)
        for ii in self.rtd:
            for jj in rtd[ii]:
                if type(jj) == type_irt and ((type_irt is str and jj.lower() == irt.lower()) or jj == irt):
                    return ii
        return 'UNKN'

    def Check(self,rt,chk='_',rt_true=True,rt_false=False):
        rtc=Get(rt,'0|rc',out='raw',err='ignore',check=(list,tuple,dict))
        nrtc=self.Trans(rtc)
        if chk != '_':
            if Trans(chk) == nrtc:
                return rt_true
            return rt_false
        return nrtc

    def Get(self,rt):
        rtc=Get(rt,'0|rc',out='raw',err='ignore',check=(list,tuple,dict))
        return self.Trans(rtc)

