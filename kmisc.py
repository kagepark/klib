#!/bin/python
# -*- coding: utf-8 -*-
# Kage personal stuff
#
from __future__ import print_function
import sys,os,re,copy
import tarfile
import tempfile
from os import close, remove
import random
import hashlib

from klib.CONVERT import CONVERT
from klib.GET import GET
from klib.STR import STR

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
url_group = re.compile('^(https|http|ftp)://([^/\r\n]+)(/[^\r\n]*)?')
#log_file=None
log_intro=3
log_new_line='\n'

cdrom_ko=['sr_mod','cdrom','libata','ata_piix','ata_generic','usb-storage']

def is_cancel(func):
    if func:
        ttt=type(func).__name__
        if ttt in ['function','instancemethod','method']:
            if func():
                return True
        elif ttt in ['bool','str'] and func:
            return True
    return False

def log_file_info(name):
    log_file_str=''
    if name and len(name) > 0:
        if type(name) is str:
            if name.split(':')[0] == 'log_file':
                return name
            name=name.split(',')
        for nn in name:
            if nn and nn != 'None':
                if log_file_str:
                    log_file_str='{}:{}'.format(log_file_str,nn)
                else:
                    log_file_str='{}'.format(nn)
        if log_file_str:
            return 'log_file:{}'.format(log_file_str)

def error_exit(msg=None):
    if msg is not None:
       print(msg)
    sys.exit(-1)


def std_err(msg,direct=False):
    if direct:
        sys.stderr.write(msg)
    else:
        sys.stderr.write('{}\n'.format(msg))
    sys.stderr.flush()
    
def dget(dict=None,keys=None):
    if dict is None or keys is None:
        return False
    tmp=dict.copy()
    for ii in keys.split('/'):
        if ii in tmp:
           dtmp=tmp[ii]
        else:
           return False
        tmp=dtmp
    return tmp

def dput(dic=None,keys=None,val=None,force=False,safe=True):
    if dic is not None and keys:
        tmp=dic
        keys_arr=keys.split('/')
        keys_num=len(keys_arr)
        for ii in keys_arr[:(keys_num-1)]:
            if ii in tmp:
                if type(tmp[ii]) == type({}):
                    dtmp=tmp[ii]
                else:
                    if tmp[ii] == None:
                        tmp[ii]={}
                        dtmp=tmp[ii]
                    else:
                        if force:
                            vtmp=tmp[ii]
                            tmp[ii]={vtmp:None}
                            dtmp=tmp[ii]
                        else:
                            return False
            else:
                if force:
                    tmp[ii]={}
                    dtmp=tmp[ii]
                else:
                    return False
            tmp=dtmp
        if val == '_blank_':
            val={}
        if keys_arr[keys_num-1] in tmp.keys():
            if safe:
                if tmp[keys_arr[keys_num-1]]:
                    return False
            tmp.update({keys_arr[keys_num-1]:val})
            return True
        else:
            if force:
                tmp.update({keys_arr[keys_num-1]:val})
                return True
    return False

def sendanmail(to,subj,msg,html=True):
    if html:
        email_msg='''To: {0}
Subject: {1}
Content-Type: text/html
<html>
<body>
<pre>
{2}
</pre>
</body>
</html>'''.format(to,subj,msg)
    else:
        email_msg=''
    cmd='''echo "{0}" | sendmail -t'''.format(email_msg)
    return rshell(cmd)

def md5(string):
    return hashlib.md5(CONVERT(string).Bytes()).hexdigest()

def cat(filename,no_end_newline=False):
    tmp=file_rw(filename)
    if isinstance(Get(tmp,1),str) and no_end_newline:
        tmp_a=tmp.split('\n')
        ntmp=''
        for ii in tmp_a[:-1]:
            if ntmp:
                ntmp='{}\n{}'.format(ntmp,ii)
            else:
                ntmp='{}'.format(ii)
        if len(tmp_a[-1]) > 0:
            ntmp='{}\n{}'.format(ntmp,tmp_a[-1])
        tmp=ntmp
    return tmp

def ls(dirname,opt=''):
    if os.path.isdir(dirname):
        dirlist=[]
        dirinfo=list(os.walk(dirname))[0]
        if opt == 'd':
            dirlist=dirinfo[1]
        elif opt == 'f':
            dirlist=dirinfo[2]
        else:
            dirlist=dirinfo[1]+dirinfo[2]
        return dirlist
    return False


def rm_file(filelist):
    if type(filelist) == type([]):
       filelist_tmp=filelist
    else:
       filelist_tmp=filelist.split(',')
    for ii in list(filelist_tmp):
        if os.path.isfile(ii):
            os.unlink(ii)
        else:
            print('not found {0}'.format(ii))

def make_tar(filename,filelist,ctype='gz',ignore_file=[]):
    if ctype == 'bz2':
        tar = tarfile.open(filename,"w:bz2")
    elif ctype == 'stream':
        tar = tarfile.open(filename,"w:")
    else:
        tar = tarfile.open(filename,"w:gz")
    ig_dupl=[]
    filelist_tmp=[]
    filelist_type=type(filelist)
    if filelist_type is list:
       filelist_tmp=filelist
    elif filelist_type is str:
       filelist_tmp=filelist.split(',')
    for ii in filelist_tmp:
        if os.path.isfile(ii):
            if ii in ignore_file or ii in ig_dupl:
                continue
            ig_dupl.append(ii)
            tar.add(ii)
        elif os.path.isdir(ii):
            for r,d,f in os.walk(ii):
                if r in ignore_file or (len(d) == 1 and d[0] in ignore_file):
                    continue
                for ff in f:
                    aa=os.path.join(r,ff)
                    if aa in ignore_file or aa in ig_dupl:
                        continue
                    ig_dupl.append(aa)
                    tar.add(aa)
        else:
            print('{} not found'.format(ii))
    tar.close()


def is_tempfile(filepath,tmp_dir='/tmp'):
   filepath_arr=filepath.split('/')
   if len(filepath_arr) == 1:
      return False
   tmp_dir_arr=tmp_dir.split('/')
   
   for ii in range(0,len(tmp_dir_arr)):
      if filepath_arr[ii] != tmp_dir_arr[ii]:
          return False
   return True


def mktemp(filename=None,suffix='-XXXXXXXX',opt='dry',base_dir='/tmp'):
   if filename is None:
       filename=os.path.join(base_dir,random_str(length=len(suffix)-1,mode='str'))
   dir_name=os.path.dirname(filename)
   file_name=os.path.basename(filename)
   name, ext = os.path.splitext(file_name)
   if type(suffix) is not str:
       suffix='-XXXXXXXX'
   num_type='.%0{}d'.format(len(suffix)-1)
   if dir_name == '.':
       dir_name=os.path.dirname(os.path.realpath(__file__))
   elif dir_name == '':
       dir_name=base_dir
   def new_name(name,ext=None,ext2=None):
       if ext:
           if ext2:
               return '{}{}{}'.format(name,ext,ext2)
           return '{}{}'.format(name,ext)
       if ext2:
           return '{}{}'.format(name,ext2)
       return name
   def new_dest(dest_dir,name,ext=None):
       if os.path.isdir(dest_dir) is False:
           return False
       i=0
       new_file=new_name(name,ext)
       while True:
           rfile=os.path.join(dest_dir,new_file)
           if os.path.exists(rfile) is False:
               return rfile
           if suffix:
               if '0' in suffix or 'n' in suffix or 'N' in suffix:
                   if suffix[-1] not in ['0','n']:
                       new_file=new_name(name,num_type%i,ext)
                   else:
                       new_file=new_name(name,ext,num_type%i)
               elif 'x' in suffix or 'X' in suffix:
                   rnd_str='.{}'.format(random_str(length=len(suffix)-1,mode='str'))
                   if suffix[-1] not in ['X','x']:
                       new_file=new_name(name,rnd_str,ext)
                   else:
                       new_file=new_name(name,ext,rnd_str)
               else:
                   if i == 0:
                       new_file=new_name(name,ext,'.{}'.format(suffix))
                   else:
                       new_file=new_name(name,ext,'.{}.{}'.format(suffix,i))
           else:
               new_file=new_name(name,ext,'.{}'.format(i))
           i+=1
   new_dest_file=new_dest(dir_name,name,ext)
   if opt in ['file','f']:
      os.mknode(new_dest_file)
   elif opt in ['dir','d','directory']:
      os.mkdir(new_dest_file)
   else:
      return new_dest_file

def get_key(dic=None,find=None):
    return find_key_from_value(dic=dic,find=find)

def find_key_from_value(dic=None,find=None):
    if isinstance(dic,dict):
        if find is None:
            return list(dic.keys())
        else:
            for key,val in dic.items():
                if val == find:
                    return key
    elif isinstance(dic,list) or isinstance(dic,tuple):
        if find is None:
            return len(dic)
        else:
            if find in dic:
                return dic.index(find)
         
def check_work_dir(work_dir,make=False,ntry=1,try_wait=[1,3]):
    for ii in range(0,ntry):
        if os.path.isdir(work_dir):
            return True
        else:
            if make:
                try:
                    os.makedirs(work_dir)
                    return True
                except:
                    sleep(try_wait)
    return False

def check_value(src,find,idx=None):
    '''Check key or value in the dict, list or tuple then True, not then False'''
    if isinstance(src, (list,tuple,str,dict)):
        if idx is None:
            if find in src:
                return True
        else:
            if isinstance(src,str):
                if idx < 0:
                    if src[idx-len(find):idx] == find:
                        return True
                else:
                    if src[idx:idx+len(find)] == find:
                        return True
            else:
                if Get(src,idx,out='raw') == find:
                    return True
    return False

def OutFormat(data,out=None):
    if out in [tuple,'tuple']:
        if not isinstance(data,tuple):
            return (data,)
        elif not isinstance(data,list):
            return tuple(data)
    elif out in [list,'list']:
        if not isinstance(data,list):
            return [data]
        elif not isinstance(data,tuple):
            return list(data)
    elif out in ['raw',None]:
        if isinstance(data,(list,tuple)) and len(data) == 1:
            return data[0]
        elif isinstance(data,dict) and len(data) == 1:
            return data.values()[0]
    return data

def Get(*inps,**opts):
    default=opts.get('default',None)
    out=opts.get('out',None)
    err=opts.get('err',True)
    check=opts.get('check',(str,list,tuple,dict))
    key=None
    if len(inps) >= 2:
        src=inps[0]
        key=inps[1:]
    elif len(inps) == 1:
        src=inps[0]
        key=opts.get('key',None)
        if isinstance(key,list):
            key=tuple(key)
        elif key is not None:
            key=(key,)
    rc=[]
    if key is None:
        if err in [True,'err','True']:
            return OutFormat(default,out=out)
        return OutFormat(src,out=out)
    if isinstance(src,tuple(check)):
        if isinstance(src,(str,list,tuple)) and len(src)>0:
            for kk in Abs(*key,obj=src,out=list,default=[None],err=False):
                if kk is None:
                    if err != 'ignore':
                        rc.append(default)
                else:
                    rc.append(src[kk])
            if not rc and err in [True,'err','True']:
                return OutFormat(default,out=out)
            return OutFormat(rc,out=out)
        elif isinstance(src,dict) and len(src) > 0:
            nkeys=Abs(*key,obj=src,out=list,default=[None],err=False)
            if nkeys:
                for kk in Abs(*key,obj=src,out=list,default=[None],err=False):
                    rr=src.get(kk,default)
                    if rr == default:
                        if err != 'ignore':
                            rc.append(rr)
                    else:
                        rc.append(rr)
                if not rc and err in [True,'err','True']:
                    return OutFormat(default,out=out)
                return OutFormat(rc,out=out)
            return src.get(key[0],default)
    elif type(src).__name__ in ['instance','classobj']:
        if isinstance(key,(list,tuple,dict)):
            for kk in key:
                rc.append(getattr(src,kk,default))
            if not rc and err in [True,'err','True']:
                return OutFormat(default,out=out)
            return OutFormat(rc,out=out)
        return getattr(src,key,default)
    if err in [True,'err','True']:
        return OutFormat(default,out=out)
    return OutFormat(src,out=out)


def get_value(src,key=None,default=None,check=[list,tuple,dict]):
    return Get(src,key,default=default,check=check)

def krc(rt,chk='_',rtd={'GOOD':[True,'True','Good','Ok','Pass',{'OK'},0],'FAIL':[False,'False','Fail',{'FAL'}],'NONE':[None,'None','N/A',{'NA'}],'IGNO':['IGNO','Ignore',{'IGN'}],'ERRO':['ERR','Error',{'ERR'}],'WARN':['Warn',{'WAR'}],'UNKN':['Unknown','UNKN',{'UNK'}],'JUMP':['Jump',{'JUMP'}]}):
    def trans(irt):
        type_irt=type(irt)
        for ii in rtd:
            for jj in rtd[ii]:
                if type(jj) == type_irt and ((type_irt is str and jj.lower() == irt.lower()) or jj == irt):
                    return ii
        return 'UNKN'
    rtc=Get(rt,'0|rc',out='raw',err='ignore',check=(list,tuple,dict))
    nrtc=trans(rtc)
    if chk != '_':
        if trans(chk) == nrtc:
            return True
        return False
    return nrtc

def get_data(data,key=None,ekey=None,default=None,method=None,strip=True,find=[],out_form=str):
    if argtype(data,'Request'):
        if key:
            if method is None:
                method=data.method
            if method.upper() == 'GET':
                rc=data.GET.get(key,default)
            elif method == 'FILE':
                if out_form is list:
                    rc=data.FILES.getlist(key,default)
                else:
                    rc=data.FILES.get(key,default)
            else:
                if out_form is list:
                    rc=data.POST.getlist(key,default)
                else:
                    rc=data.POST.get(key,default)
            if argtype(rc,str) and strip:
                rc=rc.strip()
            if rc in find:
                return True
            if rc == 'true':
                return True
            elif rc == '':
                return default
            return rc
        else:
            if data.method == 'GET':
                return data.GET
            else:
                return data.data
    else:
        type_data=type(data)
        if type_data in [tuple,list]:
            if len(data) > key:
                if ekey and len(data) > ekey:
                    return data[key:ekey]
                else:
                    return data[key]
        elif type_data is dict:
            return data.get(key,default)
    return default

def Abs(*inps,**opts):
    default=opts.get('default',None)
    out=opts.get('out','auto')
    obj=opts.get('obj',None)
    err=opts.get('err',True)
    def int_idx(idx,nobj,default,err,out='auto'):
        if idx < 0:
            if abs(idx) <= nobj:
                if out in ['list',list]:
                    return [nobj+idx]
                elif out in ['tuple',tuple]:
                    return (nobj+idx,)
                return nobj+idx
            elif err not in [True,'err','True']:
                return 0
        else:
            if nobj > idx:
                if out in ['list',list]:
                    return [idx]
                elif out in ['tuple',tuple]:
                    return (idx,)
                return idx
            elif err not in [True,'err','True']:
                return nobj-1
        return default
    if len(inps) > 0:
        ss=None
        ee=None
        rt=[]
        if obj is None:
            for i in inps:
                if isinstance(i,int):
                    rt.append(abs(i))
                elif err in [True,'err','True']:
                    rt.append(default)
        elif isinstance(obj,dict):
            keys=list(obj)
            for idx in inps:
                if isinstance(idx,int):
                    rt.append(keys[int_idx(idx,len(keys),default,err)])
                elif isinstance(idx,tuple) and len(idx) == 2:
                    ss=Abs(idx[0],**opts)
                    ee=Abs(idx[1],**opts)
                    for i in range(ss,ee+1):
                        rt.append(keys[i])
                elif isinstance(idx,str):
                    try:
                        idx=int(idx)
                        rt.append(int_idx(idx,len(keys),default,err))
                    except:
                        if len(idx.split(':')) == 2:
                            ss,ee=tuple(idx.split(':'))
                            if isinstance(ss,int) and isinstance(ee,int):
                                for i in range(ss,ee+1):
                                    rt.append(keys[i])
                        elif len(idx.split('-')) == 2:
                            ss,ee=tuple(idx.split('-'))
                            if isinstance(ss,int) and isinstance(ee,int):
                                for i in range(ss,ee+1):
                                    rt.append(keys[i])
                        elif len(idx.split('|')) > 1:
                            rt=rt+idx.split('|')
        elif isinstance(obj,(list,tuple,str)):
            nobj=len(obj)
            for idx in inps:
                if isinstance(idx,list):
                    for ii in idx:
                        if isinstance(ii,int):
                            if nobj > ii:
                                rt.append(ii)
                            else:
                                rt.append(OutFormat(default))
                elif isinstance(idx,int):
                    rt.append(int_idx(idx,nobj,default,err))
                elif isinstance(idx,tuple) and len(idx) == 2:
                    ss=Abs(idx[0],**opts)
                    ee=Abs(idx[1],**opts)
                    rt=rt+list(range(ss,ee+1))
                elif isinstance(idx,str):
                    try:
                        idx=int(idx)
                        rt.append(int_idx(idx,nobj,default,err))
                    except:
                        if len(idx.split(':')) == 2:
                            ss,ee=tuple(idx.split(':'))
                            ss=Abs(ss,**opts)
                            ee=Abs(ee,**opts)
                            if isinstance(ss,int) and isinstance(ee,int):
                                rt=rt+list(range(ss,ee+1))
                        elif len(idx.split('-')) == 2:
                            ss,ee=tuple(idx.split('-'))
                            ss=Abs(ss,**opts)
                            ee=Abs(ee,**opts)
                            if isinstance(ss,int) and isinstance(ee,int):
                                rt=rt+list(range(ss,ee+1))
                        elif len(idx.split('|')) > 1:
                            for i in idx.split('|'):
                                ss=Abs(i,obj=obj,out='raw')
                                if isinstance(ss,int):
                                    rt.append(ss)
                        else:
                            rt.append(OutFormat(default))
        return OutFormat(rt,out=out)
    elif obj:
        if isinstance(obj,(list,tuple,str)):
            return len(obj)
        elif isinstance(obj,dict):
            return list(obj.keys())
    return default

def Delete(*inps,**opts):
    if len(inps) >= 2:
        obj=inps[0]
        keys=inps[1:]
    elif len(inps) == 1:
        obj=inps[0]
        keys=opts.get('key',None)
        if isinstance(keys,list):
            keys=tuple(keys)
        elif keys is not None:
            keys=(keys,)
    default=opts.get('default',None)
    _type=opts.get('type','index')
   
    if isinstance(obj,(list,tuple)):
        nobj=len(obj)
        rt=[]
        if _type == 'index':
            nkeys=Abs(*tuple(keys),obj=obj,out=list)
            for i in range(0,len(obj)):
                if i not in nkeys:
                    rt.append(obj[i])
        else:
            for i in obj:
                if i not in keys:
                    rt.append(i)
        return rt
    elif isinstance(obj,dict):
        if isinstance(keys,(list,tuple,dict)):
            for key in keys:
                obj.pop(key,default)
        else:
            obj.pop(keys,default)
        return obj
    elif isinstance(obj,str):
        nkeys=[]
        for i in keys:
            if isinstance(i,(tuple,str,int)):
                tt=Abs(i,obj=obj,out=list)
                if tt:
                    nkeys=nkeys+tt
        rt=''
        for i in range(0,len(obj)):
            if i in nkeys:
                continue
            rt=rt+obj[i]
        return rt
    return default

if __name__ == "__main__":
    class ABC:
        uu=3
        def __init__(self):
            self.a=1
            self.b=2
    print(get_value(ABC(),'b',default=None))
    print(get_value(ABC(),'uu',default=None))
    print(get_value(ABC(),'ux',default=None))

    a=[0,1,2,3]
    print(get(a,1,-8,3,-2))
