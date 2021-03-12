# Kage Park
import sys
import json as _json
import pickle
from klib.kmisc import * # import kmisc(file)'s each function to local module's function
import filetype

class IS:
    def __init__(self,src=None,**opts):
        self.src=src
        self.rtd=opts.get('rtd',{'GOOD':[True,'True','Good','Ok','Pass',{'OK'},0],'FAIL':[False,'False','Fail',{'FAL'}],'NONE':[None,'None','N/A',{'NA'}],'IGNO':['IGNO','Ignore',{'IGN'}],'ERRO':['ERR','Error',{'ERR'}],'WARN':['Warn',{'WAR'}],'UNKN':['Unknown','UNKN',{'UNK'}],'JUMP':['Jump',{'JUMP'}]})

    def Py2(self):
        if sys.version_info[0] < 3:
            return True
        return False

    def Py3(self):
        if sys.version_info[0] >= 3:
            return True
        return False

    def Int(self):
        try:
            int(self.src)
            return True
        except:
            return False

    def Ipv4(self):
        if isinstance(self.src,str):
            ipa = self.src.strip().split(".")
            if len(ipa) != 4: return False
            for ip in ipa:
                if not ip.isdigit() or not 0 <= int(ip) <= 255: return False
            return True
        elif isinstance(self.src,int):
            pass
        return False

    def Mac4(self,**opts):
        symbol=opts.get('symbol',':')
        default=opts.get('default',False)
        if isinstance(self.src,str):
            self.src=self.src.strip()
            # make sure the format
            if 12 <= len(self.src) <= 17:
                for i in [':','-']:
                    self.src=self.src.replace(i,'')
                self.src=symbol.join(self.src[i:i+2] for i in range(0,12,2))
            # Check the normal mac format
            octets = self.src.split(symbol)
            if len(octets) != 6: return False
            for i in octets:
                try:
                   if len(i) != 2 or int(i, 16) > 255:
                       return False
                except:
                   return False
            return True
        return default

        
    def Ip_with_port(self,port,**opts):
        default=opts.get('default',False)
        tcp_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_sk.settimeout(1)
        if self.ipv4(self.src) is False or not isinstance(port,(str,int,list,tuple)):
            return default
        if isinstance(port,(str,int)):
            try:
                port=[int(port)]
            except:
                return default
        for pt in port:
            try:
                tcp_sk.connect((self.src,pt))
                return True
            except:
                pass
        return False

    def Ip_in_range(self,start,end,**opts):
        default=opts.get('default',False)
        if self.ipv4(self.src) and self.ipv4(start) and self.ipv4(end):
            if ip2num(start) <= ip2num(self.src) <= ip2num(end):
                return True
            return False
        return default

    def File(self):
        if isinstance(self.src,str): return os.path.isfile(self.src)
        return False

    def Dir(self):
        if isinstance(self.src,str): return os.path.isdir(self.src)
        return False

    def Xml(self):
        firstLine=file_rw(self.src,out='string',read='firstline')
        if firstLine is False:
            filename_str=_u_byte2str(self.src)
            if isinstance(filename_str,str):
                firstLine=filename_str.split('\n')[0]
        if isinstance(firstLine,str) and firstLine.split(' ')[0] == '<?xml': return True
        return False

    def Json(self):
        try:
            _json.loads(self.src)
            return True
        except:
            return False

    def Matrix(self,**opts):
        default=opts.get('default',False)
        if isinstance(self.src,(tuple,list)) and len(self.src) >= 1:
            if isinstance(self.src[0],(tuple,list)): # |a,b,c|
                first_ln=len(self.src[0])            # |d,e,f|
                for ii in self.src[1:]:
                    if isinstance(ii,(tuple,list)) and len(ii) == first_ln: continue
                    return False
                return True
            else: # |a,b,c,d|
                first_typ=type(self.src[0])
                for ii in self.src[1:]:
                    if type(ii) != first_type: return False
                return True
        return default

    def Lost_network(self,**opts):
        default=opts.get('default',False)
        timeout_sec=opts.get('timeout',1800)
        interval=opts.get('interval',2)
        keep_good=opts.get('keep_good',30)
        cancel_func=opts.get('cancel_func',None)
        log=opts.get('log',None)
        init_time=None
        if self.ipv4():
            if not ping(self.src,count=3):
                if not ping(self.src,count=0,timeout=timeout_sec,keep_good=keep_good,interval=interval,cancel_func=cancel_func,log=log):
                    return True
            return False
        return default

    def Comback_network(self,**opts):
        default=opts.get('default',False)
        timeout_sec=opts.get('timeout',1800)
        interval=opts.get('interval',3)
        keep=opts.get('keep',20)
        cancel_func=opts.get('cancel_func',None)
        log=opts.get('log',None)
        init_time=None
        run_time=int_sec()
        if self.ipv4(self.src):
            if log:
                log('[',direct=True,log_level=1)
            while True:
                ttt,init_time=timeout(timeout_sec,init_time)
                if ttt:
                    if log:
                        log(']\n',direct=True,log_level=1)
                    return False,'Timeout monitor'
                if self.cancel(cancel_func):
                    if log:
                        log(']\n',direct=True,log_level=1)
                    return True,'Stopped monitor by Custom'
                if ping(self.src,cancel_func=cancel_func):
                    if (int_sec() - run_time) > keep:
                        if log:
                            log(']\n',direct=True,log_level=1)
                        return True,'OK'
                    if log:
                        log('-',direct=True,log_level=1)
                else:
                    run_time=int_sec()
                    if log:
                        log('.',direct=True,log_level=1)
                time.sleep(interval)
            if log:
                log(']\n',direct=True,log_level=1)
            return False,'Timeout/Unknown issue'
        return default,'IP format error'

    def Rc(self,chk='_'):
        def trans(irt):
            type_irt=type(irt)
            for ii in rtd:
                for jj in rtd[ii]:
                    if type(jj) == type_irt and ((type_irt is str and jj.lower() == irt.lower()) or jj == irt):
                        return ii
            return 'UNKN'
        rtc=Get(self.src,'0|rc',out='raw',err='ignore',check=(list,tuple,dict))
        nrtc=trans(rtc)
        if chk != '_':
            if trans(chk) == nrtc:
                return True
            return False
        return nrtc

    def Cancel(self,func=None):
        if func is None:
            func=self.src
        ttt=type(func).__name__
        if ttt in ['function','instancemethod','method']:
            if func():
                return True
        elif ttt in ['bool','str'] and func in [True,'cancel']:
            return True
        return False

    def Window(self):
        return False

    def Android(self):
        return False

    def IOS(self):
        return False

    def Centos(self):
        return False

    def Unbuntu(self):
        return False

    def Suse(self):
        return False

    def Linux(self):
        if self.centos() or self.ubuntu() or self.suse(): return True
        return False

    def Type(self,default=None):
        if isinstance(self.src,str) and os.path.isfile(self.src):
            aa=filetype.guess(self.src) 
            if aa: return aa.__dict__.get('_Type__extension')
            try:
                with open(self.src,'rb') as f:
                    pickle.load(f)
                    return 'pickle'
            except:
                pass
            return default
        else:
            try:
                return type(self.src).__name__
            except:
                return default
