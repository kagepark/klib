#!/bin/python
# -*- coding: utf-8 -*-
# Kage personal stuff
#
from __future__ import print_function
import sys,os,re,subprocess,traceback,copy
import tarfile
import tempfile
import inspect
import time
from datetime import datetime
from os import close, remove
import random
import fcntl,socket, struct
import pickle
from threading import Thread
import base64
import hashlib
import multiprocessing
import requests
import json
import uuid
from pprint import pprint
import ast
import zlib
import base64

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
url_group = re.compile('^(https|http|ftp)://([^/\r\n]+)(/[^\r\n]*)?')
#log_file=None
log_intro=3
log_new_line='\n'

cdrom_ko=['sr_mod','cdrom','libata','ata_piix','ata_generic','usb-storage']

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
    
def timechk(time='0',wait='0',tformat=None):
    if tformat is None:
        now=int(datetime.now().strftime('%s'))
    else:
        if time == '0':
            now=datetime.now().strftime(tformat)
        else:
            now=int(datetime.strptime(str(time),tformat).strftime('%s'))

    if tformat is None and str(time).isdigit() and int(time) > 0 and int(wait) > 0:
        if now - int(time) > int(wait):
            return False
        else:
            return True
    else:
        return now

def get_caller_fcuntion_name(detail=False):
    try:
        dep=len(inspect.stack())-2
        if detail:
            return sys._getframe(dep).f_code.co_name,sys._getframe(dep).f_lineno,sys._getframe(dep).f_code.co_filename
        else:
            name=sys._getframe(dep).f_code.co_name
            if name == '_bootstrap_inner' or name == '_run_code':
                return sys._getframe(3).f_code.co_name
            return name
    except:
        return False

def log_format(*msg,**opts):
    log_date_format=opts.get('log_date_format','[%m/%d/%Y %H:%M:%S]')
    func_name=opts.get('func_name',False)
    log_intro=opts.get('log_intro',3)
    end_new_line=opts.get('end_new_line','')
    start_new_line=opts.get('start_new_line','\n')
    if len(msg) > 0:
        m_str=None
        intro=''
        intro_space=''
        if log_date_format or log_intro > 2:
            intro=timechk(tformat=log_date_format)+' '
        if func_name or log_intro > 1:
            if type(func_name) is str:
                intro=intro+'{0}() '.format(func_name)
            else:
                intro=intro+'{0}() '.format(get_caller_fcuntion_name())
        if intro:
           for i in range(0,len(intro)+1):
               intro_space=intro_space+' '
        for m in list(msg):
            if m_str is None:
                m_str='{0}{1}{2}{3}'.format(start_new_line,intro,m,end_new_line)
            else:
                m_str='{0}{1}{2}{3}{4}'.format(start_new_line,m_str,intro_space,m,end_new_line)
        return m_str

def logging(*msg,**opts):
    return printf(*msg,**opts)

def printf(*msg,**opts):
    log_p=False
    log=opts.get('log',None)
    log_level=opts.get('log_level',8)
    dsp=opts.get('dsp','a')
    date=opts.get('date',False)
    date_format=opts.get('date_format','%m/%d/%Y %H:%M:%S')
    intro=opts.get('intro',None)
    caller=opts.get('caller',False)
    caller_detail=opts.get('caller_detail',False)
    msg=list(msg)
    direct=opts.get('direct',False)
    color=opts.get('color',None)
    color_db=opts.get('color_db',{'blue': 34, 'grey': 30, 'yellow': 33, 'green': 32, 'cyan': 36, 'magenta': 35, 'white': 37, 'red': 31})
    bg_color=opts.get('bg_color',None)
    bg_color_db=opts.get('bg_color_db',{'cyan': 46, 'white': 47, 'grey': 40, 'yellow': 43, 'blue': 44, 'magenta': 45, 'red': 41, 'green': 42})
    attr=opts.get('attr',None)
    attr_db=opts.get('attr_db',{'reverse': 7, 'blink': 5,'concealed': 8, 'underline': 4, 'bold': 1})
    syslogd=opts.get('syslogd',None)

    if direct:
        new_line=opts.get('new_line','')
    else:
        new_line=opts.get('new_line','\n')
    logfile=opts.get('logfile',None)
    logfile_type=type(logfile)
    if logfile_type is str:
        logfile=logfile.split(',')
    elif logfile_type in [list,tuple]:
        logfile=list(logfile)
    else:
        logfile=[]
    for ii in msg:
        if type(ii) is str and ':' in ii:
            logfile_list=ii.split(':')
            if logfile_list[0] in ['log_file','logfile']:
                if len(logfile_list) > 2:
                    for jj in logfile_list[1:]:
                        logfile.append(jj)
                else:
                    logfile=logfile+logfile_list[1].split(',')
                msg.remove(ii)

    if os.getenv('ANSI_COLORS_DISABLED') is None and (color or bg_color or attr):
        reset='''\033[0m'''
        fmt_msg='''\033[%dm%s'''
        if color and color in color_db:
            msg=fmt_msg % (color_db[color],msg)
        if bg_color and bg_color in bg_color_db:
            msg=fmt_msg % (color_db[bg_color],msg)
        if attr and attr in attr_db:
            msg=fmt_msg % (attr_db[attr],msg)
        msg=msg+reset

    # Make a Intro
    intro_msg=''
    if date and syslogd is False:
        intro_msg='[{0}] '.format(datetime.now().strftime(date_format))
    if caller:
        call_name=get_caller_fcuntion_name(detail=caller_detail)
        if call_name:
            if len(call_name) == 3:
                intro_msg=intro_msg+'{}({}:{}): '.format(call_name[0],call_name[1],call_name[2])
            else:
                intro_msg=intro_msg+'{}(): '.format(call_name)
    if intro is not None:
        intro_msg=intro_msg+intro+': '

    # Make a Tap
    tap=''
    for ii in range(0,len(intro_msg)):
        tap=tap+' '

    # Make a msg
    msg_str=''
    for ii in msg:
        if msg_str:
            if new_line:
                msg_str=msg_str+new_line+tap+'{}'.format(ii)
            else:
                msg_str=msg_str+'{}'.format(ii)
        else:
            msg_str=intro_msg+'{}'.format(ii)

    # save msg to syslogd
    if syslogd:
        if syslogd in ['INFO','info']:
            syslog.syslog(syslog.LOG_INFO,msg)
        elif syslogd in ['KERN','kern']:
            syslog.syslog(syslog.LOG_KERN,msg)
        elif syslogd in ['ERR','err']:
            syslog.syslog(syslog.LOG_ERR,msg)
        elif syslogd in ['CRIT','crit']:
            syslog.syslog(syslog.LOG_CRIT,msg)
        elif syslogd in ['WARN','warn']:
            syslog.syslog(syslog.LOG_WARNING,msg)
        elif syslogd in ['DBG','DEBUG','dbg','debug']:
            syslog.syslog(syslog.LOG_DEBUG,msg)
        else:
            syslog.syslog(msg)

    # Save msg to file
    if type(logfile) is str:
        logfile=logfile.split(',')
    if type(logfile) in [list,tuple] and ('f' in dsp or 'a' in dsp):
        for ii in logfile:
            if ii and os.path.isdir(os.path.dirname(ii)):
                log_p=True
                with open(ii,'a+') as f:
                    f.write(msg_str+new_line)
    if type(log).__name__ == 'function':
         log_func_arg=get_function_args(log,mode='all')
         if 'args' in log_func_arg or 'varargs' in log_func_arg:
             log_p=True
             args=log_func_arg.get('args',[])
             if args and len(args) <= 3 and ('direct' in args or 'log_level' in args):
                 tmp=[]
                 for i in range(0,len(args)):
                     tmp.append(i)
                 if 'direct' in args:
                     didx=args.index('direct')
                     del tmp[didx]
                     args[didx]=direct
                 if 'log_level' in args:
                     lidx=args.index('log_level')
                     del tmp[lidx]
                     args[lidx]=log_level
                 args[tmp[0]]=msg_str
                 log(*args)
             elif 'keywards' in log_func_arg:
                 log(msg_str,direct=direct,log_level=log_level)
             elif 'defaults' in log_func_arg:
                 if 'direct' in log_func_arg['defaults'] and 'log_level' in log_func_arg['defaults']:
                     log(msg_str,direct=direct,log_level=log_level)
                 elif 'log_level' in log_func_arg['defaults']:
                     log(msg_str,log_level=log_level)
                 elif 'direct' in log_func_arg['defaults']:
                     log(msg_str,direct=direct)
                 else:
                     log(msg_str)
             else:
                 log(msg_str)
    # print msg to screen
    if (log_p is False and 'a' in dsp) or 's' in dsp or 'e' in dsp:
         if 'e' in dsp:
             sys.stderr.write(msg_str+new_line)
         else:
             sys.stdout.write(msg_str+new_line)
         sys.stdout.flush()
    # return msg
    if 'r' in dsp:
         return msg_str


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

def is_py3():
    if sys.version_info[0] >= 3:
        return True
    return False


def rshell(cmd,timeout=None,ansi=True,path=None):
    start_time=datetime.now().strftime('%s')
    if type(cmd) is not str:
        return -1,'wrong command information :{0}'.format(cmd),'',start_time,start_time,datetime.now().strftime('%s'),cmd,path
    Popen=subprocess.Popen
    PIPE=subprocess.PIPE
    cmd_env=''
    if path is not None:
        cmd_env='''export PATH=%s:${PATH}\n[ -d %s ] && cd %s\n'''%(path,path,path)
    p = Popen(cmd_env+cmd , shell=True, stdout=PIPE, stderr=PIPE)
    out=None
    err=None
    if timeout:
        try:
            timeout=int(timeout)
        except:
            timeout=600
        if timeout < 3:
            timeout=3
    if is_py3():
        try:
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            return -1, 'Kill process after timeout ({0} sec)'.format(timeout), 'Error: Kill process after Timeout {0}'.format(timeout),start_time,datetime.now().strftime('%s'),cmd,path
    else:
        if timeout:
            countdown=int('{}'.format(timeout))
            while p.poll() is None and countdown > 0:
                time.sleep(2)
                countdown -= 2
            if countdown < 1:
                p.kill()
                return -1, 'Kill process after timeout ({0} sec)'.format(timeout), 'Error: Kill process after Timeout {0}'.format(timeout),start_time,datetime.now().strftime('%s'),cmd,path
        out, err = p.communicate()

    if is_py3():
        out=out.decode("ISO-8859-1")
        err=err.decode("ISO-8859-1")
    if ansi:
        return p.returncode, out.rstrip(), err.rstrip(),start_time,datetime.now().strftime('%s'),cmd,path
    else:
        return p.returncode, ansi_escape.sub('',out).rstrip(), ansi_escape.sub('',err).rstrip(),start_time,datetime.now().strftime('%s'),cmd,path

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

def mac2str(mac,case='lower'):
    if is_mac4(mac):
        if case == 'lower':
            mac=mac.strip().replace(':','').replace('-','').lower()
        else:
            mac=mac.strip().replace(':','').replace('-','').upper()
    return mac

def str2mac(mac,sym=':',case='lower'):
    if type(mac) is str:
        cmac=mac.strip()
        if len(cmac) in [12,17]:
            cmac=cmac.replace(':','').replace('-','')
            if len(cmac) == 12:
                cmac=sym.join(cmac[i:i+2] for i in range(0,12,2))
            if case == 'lower':
                mac=cmac.lower()
            else:
                mac=cmac.upper()
    return mac

def is_mac4(mac=None,symbol=':'):
    mac=str2mac(mac,sym=symbol)
    if mac is None or type(mac) is not str:
        return False
    octets = mac.split(symbol)
    if len(octets) != 6:
        return False
    for i in octets:
        try:
           if len(i) != 2 or int(i, 16) > 255:
               return False
        except:
           return False
    return True

def sreplace(pattern,sub,string):
    return re.sub('^%s' % pattern, sub, string)

def ereplace(pattern,sub,string):
    return re.sub('%s$' % pattern, sub, string)

def md5(string):
    return hashlib.md5(_u_bytes(string)).hexdigest()

def ipv4(ipaddr=None):
    if type(ipaddr) is str:
        ipaddr_a=ipaddr.strip().split('.')
        new_ip=''
        for i in ipaddr_a:
            for j in range(0,10):
                if len(i) <= 1:
                    break
                i=sreplace('^0','',i)
            if new_ip:
                new_ip+='.{}'.format(i)
            else:
                new_ip=i
        if len(new_ip.split('.')) == 4:
            return new_ip
    return False

def is_ipmi_ip(ipadd):
    tcp_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sk.settimeout(1)
    try:
        tcp_sk.connect((ipadd,623))
        return True
    except:
        return False

def is_ipv4(ipadd=None):
    if ipadd is None or type(ipadd) is not str or len(ipadd) == 0:
        return False
    ipa = ipadd.split(".")
    if len(ipa) != 4:
        return False
    for ip in ipa:
        if not ip.isdigit():
            return False
        if not 0 <= int(ip) <= 255:
            return False
    return True

def ip2num(ip):
    if is_ipv4(ip):
        return struct.unpack("!L", socket.inet_aton(ip))[0]
    return False

def ip_in_range(ip,start,end):
    if type(ip) is str and type(start) is str and type(end) is str:
        ip=ip2num(ip)
        start=ip2num(start)
        end=ip2num(end)
        if start <= ip and ip <= end:
            return True
    return False

def get_function_name():
    return traceback.extract_stack(None, 2)[0][2]

def ipmi_cmd(cmd,ipmi_ip=None,ipmi_user='ADMIN',ipmi_pass='ADMIN',log=None):
    if ipmi_ip is None:
        ipmi_str=""" ipmitool {0} """.format(cmd)
    else:
        ipmi_str=""" ipmitool -I lanplus -H {0} -U {1} -P '{2}' {3} """.format(ipmi_ip,ipmi_user,ipmi_pass,cmd)
    if log:
        log(' ipmi_cmd():{}'.format(ipmi_str),log_level=7)
    return rshell(ipmi_str)

def get_ipmi_mac(ipmi_ip=None,ipmi_user='ADMIN',ipmi_pass='ADMIN'):
    ipmi_mac_str=None
    if ipmi_ip is None:
        ipmi_mac_str=""" ipmitool lan print 2>/dev/null | grep "MAC Address" | awk """
    elif is_ipv4(ipmi_ip):
        ipmi_mac_str=""" ipmitool -I lanplus -H {0} -U {1} -P {2} lan print 2>/dev/null | grep "MAC Address" | awk """.format(ipmi_ip,ipmi_user,ipmi_pass)
    if ipmi_mac_str is not None:
        ipmi_mac_str=ipmi_mac_str + """ '{print $4}' """
        return rshell(ipmi_mac_str)

def get_ipmi_ip():
    return rshell('''ipmitool lan print 2>/dev/null| grep "IP Address" | grep -v Source | awk '{print $4}' ''')

def get_host_name():
    return socket.gethostname()

def get_host_ip(ifname=None):
    if ifname:
        return get_net_dev_ip(ifname)
    else:
        return socket.gethostbyname(socket.gethostname())

def get_dev_mac(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])
    except:
        return

def get_host_mac(ip=None,dev=None):
    if is_ipv4(ip):
        dev_info=get_net_device()
        for dev in dev_info.keys():
            if get_net_dev_ip(dev) == ip:
                return dev_info[dev]['mac']
    elif dev:
        return get_dev_mac(dev)
    else:
        #return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        return str2mac('%012x' % uuid.getnode())

def get_net_dev_ip(ifname):
    if os.path.isdir('/sys/class/net/{}'.format(ifname)) is False:
        return False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except:
        try:
            return os.popen('ip addr show {}'.format(ifname)).read().split("inet ")[1].split("/")[0]
        except:
            return

def cat(filename,no_end_newline=False):
    if os.path.isfile(filename):
        try:
            with open(filename,'rb') as f:
                tmp=f.read()
            if no_end_newline:
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
        except:
            #print('Can not read {}'.format(filename))
            pass
    return False

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

def get_net_device(name=None):
    net_dev={}
    net_dir='/sys/class/net'
    if os.path.isdir(net_dir):
        dirpath,dirnames,filenames = list(os.walk(net_dir))[0]
        if name:
            if name in dirnames:
                drv=ls('{}/{}/device/driver/module/drivers'.format(dirpath,name))
                if drv is False:
                    drv='unknown'
                else:
                    drv=drv[0].split(':')[1]
                net_dev[name]={
                    'mac':cat('{}/{}/address'.format(dirpath,name),no_end_newline=True),
                    'duplex':cat('{}/{}/duplex'.format(dirpath,name),no_end_newline=True),
                    'mtu':cat('{}/{}/mtu'.format(dirpath,name),no_end_newline=True),
                    'state':cat('{}/{}/operstate'.format(dirpath,name),no_end_newline=True),
                    'speed':cat('{}/{}/speed'.format(dirpath,name),no_end_newline=True),
                    'id':cat('{}/{}/ifindex'.format(dirpath,name),no_end_newline=True),
                    'driver':drv,
                    'drv_ver':cat('{}/{}/device/driver/module/version'.format(dirpath,name),no_end_newline=True),
                    }
        else:
            for dev in dirnames:
                drv=ls('{}/{}/device/driver/module/drivers'.format(dirpath,dev))
                if drv is False:
                    drv='unknown'
                else:
                    drv=drv[0].split(':')[1]
                net_dev[dev]={
                    'mac':cat('{}/{}/address'.format(dirpath,dev),no_end_newline=True),
                    'duplex':cat('{}/{}/duplex'.format(dirpath,dev),no_end_newline=True),
                    'mtu':cat('{}/{}/mtu'.format(dirpath,dev),no_end_newline=True),
                    'state':cat('{}/{}/operstate'.format(dirpath,dev),no_end_newline=True),
                    'speed':cat('{}/{}/speed'.format(dirpath,dev),no_end_newline=True),
                    'id':cat('{}/{}/ifindex'.format(dirpath,dev),no_end_newline=True),
                    'driver':drv,
                    'drv_ver':cat('{}/{}/device/driver/module/version'.format(dirpath,dev),no_end_newline=True),
                    }
        return net_dev
    else:
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


def cut_string(string,len1=None,len2=None):
    if type(string) != str:
       string='{0}'.format(string)
    str_len=len(string)
    
    if len1 is None or len1 >= str_len:
       return [string]
       
    if len2 is None:
        rc=[string[i:i + len1] for i in range(0, str_len, len1)]
        return rc
    rc=[]
    rc.append(string[0:len1])
    string_tmp=string[len1:]
    string_tmp_len=len(string_tmp)
    for i in range(0, int(string_tmp_len/len2)+1):
        if (i+1)*len2 > string_tmp_len:
           rc.append(string_tmp[len2*i:])
        else:
           rc.append(string_tmp[len2*i:(i+1)*len2])
    return rc

def is_tempfile(filepath,tmp_dir='/tmp'):
   filepath_arr=filepath.split('/')
   if len(filepath_arr) == 1:
      return False
   tmp_dir_arr=tmp_dir.split('/')
   
   for ii in range(0,len(tmp_dir_arr)):
      if filepath_arr[ii] != tmp_dir_arr[ii]:
          return False
   return True


def mktemp(prefix='tmp-',suffix=None,opt='dry'):
   dir=os.path.dirname(prefix)
   if dir == '.':
       dir=os.path.realpath(__file__)
   elif dir == '':
       dir='/tmp'

   pfilename, file_ext = os.path.splitext(prefix)
   filename=os.path.basename(pfilename)
   if suffix is not None:
       if len(file_ext) == 0:
          file_ext='.{0}'.format(suffix)

   dest_file='{0}/{1}{2}'.format(dir,filename,file_ext)
   if opt == 'file':
      if os.path.exists(dest_file):
          return tempfile.TemporaryFile(prefix='{0}-'.format(filename),suffix=file_ext,dir=dir)
      else:
          os.mknod(dest_file)
          return dest_file
   elif opt == 'dir':
      if os.path.exists(dest_file):
          return tempfile.TemporaryDirectory(suffix='{0}-'.format(filename),prefix=prefix,dir=dir)
      else:
          os.mkdir(dest_file)
          return dest_file
   else:
      if os.path.exists(dest_file):
         return tempfile.mktemp(prefix='{0}-'.format(filename),suffix=file_ext,dir=dir)
      else:
         return dest_file

def append2list(*inp,**cond):
   org=[]
   add_num=len(inp)
   uniq=cond.get('uniq',False)
   if add_num == 0:
       return []
   src=inp[0]
   src_type=type(inp)
   if add_num == 1:
       if src_type in [list,tuple,str]:
           return list(src)
       else:
           org.append(src)
           return org
   add=inp[1:]
   if src_type is str:
      for jj in src.split(','):
         if uniq:
             if jj not in org:
                 org.append(jj)
         else:
             org.append(jj)
   elif src_type in [list,tuple]:
      for jj in src:
          if uniq:
              if jj not in org:
                  org.append(jj)
          else:
              org.append(jj)
   else:
      org.append(src)

   for ii in add:
      ii_type=type(ii)
      if ii_type in [list,tuple]:
         for jj in ii:
             if uniq:
                if jj not in org:
                    org.append(jj)
             else:
                org.append(jj)
      elif ii_type is str:
         for jj in ii.split(','):
            if uniq:
                if jj not in org:
                    org.append(jj)
            else:
                org.append(jj)
      else:
         if uniq:
            if ii not in org:
                org.append(ii)
         else:
            org.append(ii)
   return org


def isfile(filename=None):
   if filename is None:
      return False
   if len(filename) == 0:
      return False
   if os.path.isfile(filename):
      return True
   return False


def ping(host,test_num=3,retry=1,wait=1,keep=0, timeout=60,lost_mon=False,log=None,stop_func=None,stop_arg={}):
    init_sec=int_sec()
    chk_sec=int_sec()
    log_type=type(log).__name__
    found_lost=False
    if keep > 0:
       if timeout < keep:
           timeout=keep+(2*wait)
       if retry * wait < timeout:
           retry=timeout//wait + 3
    for i in range(0,retry):
       if stop_func and type(stop_arg) is dict:
           if stop_func(**stop_arg) is True:
               if log_type == 'function':
                   log(' - Stopped ping')
               return False
       rc=rshell("ping -c {0} {1}".format(test_num,host))
       if rc[0] == 0:
          if found_lost is True or int_sec() - chk_sec >= keep:
              return True
       else:
          if lost_mon:
              found_lost=True
          chk_sec=int_sec()
       if log_type == 'function':
          log(' - Re-trying ping [{}/{}]'.format(i,retry))
       if int_sec() - init_sec > timeout:
           return False
       time.sleep(wait)
    return False


def get_function_args(func,mode='defaults'):
    rc={}
    args, varargs, keywords, defaults = inspect.getargspec(func)
    if defaults is not None:
        defaults=dict(zip(args[-len(defaults):], defaults))
        del args[-len(defaults):]
        rc['defaults']=defaults
    if args:
        rc['args']=args
    if varargs:
        rc['varargs']=varargs
    if keywords:
        rc['keywards']=keywords
    if mode in ['*','all']:
        return rc
    if mode in rc:
        return rc[mode]

def get_function_list(objName=None,obj=None):
    aa={}
    if obj is None and objName is not None:
       obj=sys.modules[objName]
    if obj is not None:
        for name,fobj in inspect.getmembers(obj):
            if inspect.isfunction(fobj): # inspect.ismodule(obj) check the obj is module or not
                aa.update({name:fobj})
    return aa

def space(space_num=0,_space_='   '):
    space_str=''
    for ii in range(space_num):
        space_str='{0}{1}'.format(space_str,_space_)
    return space_str

def tap_print(string,bspace='',rc=False,NFLT=False):
    rc_str=None
    if type(string) is str:
        for ii in string.split('\n'):
            if NFLT:
               line='%s'%(ii)
               NFLT=False
            else:
               line='%s%s'%(bspace,ii)
            if rc_str is None:
               rc_str='%s'%(line)
            else:
               rc_str='%s\n%s'%(rc_str,line)
    else:
        rc_str='%s%s'%(bspace,string)

    if rc:
        return rc_str
    else:
        print(rc_str)

def str_format_print(string,rc=False):
    if type(string) is str:
        if len(string.split("'")) > 1:
            rc_str='"%s"'%(string)
        else:
            rc_str="'%s'"%(string)
    else:
        rc_str=string
    if rc:
        return rc_str
    else:
        print(rc_str)

def format_print(string,rc=False,num=0,bstr=None,NFLT=False):
    string_type=type(string)
    rc_str=''
    chk=None
    bspace=space(num)

    # Start Symbol
    if string_type is tuple:
        if bstr is None:
            if NFLT:
                rc_str='%s('%(rc_str)
            else:
                rc_str='%s%s('%(bspace,rc_str)
        else:
            rc_str='%s,\n%s%s('%(bstr,bspace,rc_str)
    elif string_type is list:
        if bstr is None:
            if NFLT:
                rc_str='%s['%(rc_str)
            else:
                rc_str='%s%s['%(bspace,rc_str)
        else:
            rc_str='%s,\n%s%s['%(bstr,bspace,rc_str)
    elif string_type is dict:
        if bstr is None:
            rc_str='%s{'%(rc_str)
        else:
            rc_str='%s,\n%s %s{'%(bstr,bspace,rc_str)
    rc_str='%s\n%s '%(rc_str,bspace)

    # Print string
    if string_type is list or string_type is tuple:
       for ii in list(string):
           ii_type=type(ii)
           if ii_type is tuple or ii_type is list or ii_type is dict:
               if not ii_type is dict:
                  num=num+1
               rc_str=format_print(ii,num=num,bstr=rc_str,rc=True)
           else:
               if chk == None:
                  rc_str='%s%s'%(rc_str,tap_print(str_format_print(ii,rc=True),rc=True))
                  chk='a'
               else:
                  rc_str='%s,\n%s'%(rc_str,tap_print(str_format_print(ii,rc=True),bspace=bspace+' ',rc=True))
    elif string_type is dict:
       for ii in string.keys():
           ii_type=type(string[ii])
           if ii_type is dict or ii_type is tuple or ii_type is list:
               num=num+1
               if ii_type is dict:
                   tmp=format_print(string[ii],num=num,rc=True)
               else:
                   tmp=format_print(string[ii],num=num,rc=True,NFLT=True)
               rc_str="%s,\n%s %s:%s"%(rc_str,bspace,str_format_print(ii,rc=True),tmp)
           else:
               if chk == None:
                  rc_str='%s%s'%(rc_str,tap_print("{0}:{1}".format(str_format_print(ii,rc=True),str_format_print(string[ii],rc=True)),rc=True))
                  chk='a'
               else:
                  rc_str='%s,\n%s'%(rc_str,tap_print("{0}:{1}".format(str_format_print(ii,rc=True),str_format_print(string[ii],rc=True)),bspace=bspace+' ',rc=True))

    # End symbol
    if string_type is tuple:
        rc_str='%s\n%s)'%(rc_str,bspace)
    elif string_type is list:
        rc_str='%s\n%s]'%(rc_str,bspace)
    elif string_type is dict:
        if bstr is None:
            rc_str='%s\n%s}'%(rc_str,bspace)
        else:
            rc_str='%s\n%s }'%(rc_str,bspace)

    else:
       rc_str=string

    # Output
    if rc:
       return rc_str    
    else:
       print(rc_str)


def str2url(string):
    if type(string) is str:
        return string.replace('+','%2B').replace('?','%3F').replace('/','%2F').replace(':','%3A').replace('=','%3D').replace(' ','+')
    return string

def clear_version(string):
    arr=string.split('.')
    if arr[-1] == '00' or arr[-1] == '0':
        arr.pop(-1)
#    for i in range(0,len(arr)):
#        if int(arr[-1]) == 0:
#            arr.pop(-1)
    new_ver=''
    for i in arr:
        if len(new_ver) > 0:
            new_ver='{0}.{1}'.format(new_ver,i)
        else:
            new_ver='{0}'.format(i)
    return new_ver 
    

def find_key_from_value(dic=None,find=None):
    if type(dic) is dict and find is not None:
        for key,val in dic.items():
            if val == find:
                return key

def random_str(length=8,strs='0aA-1b+2Bc=C3d_D,4.eE?5"fF6g7G!h8H@i9#Ij$JkK%lLmMn^N&oO*p(Pq)Q/r\Rs:St;TuUv{V<wW}x[Xy>Y]z|Z'):
    new=''
    strn=len(strs)-1
    for i in range(0,length):
        new='{0}{1}'.format(new,strs[random.randint(0,strn)])
    return new

def power_state(ipmi_ip,ipmi_user='ADMIN',ipmi_pass='ADMIN',wait_time=60,check_status=None,monitor_time=3,log_file=None,log=None):
    sys_status='unknown'
    if check_status is None:
        wait_time=3
    for ii in range(0,wait_time):
        power_status=ipmi_cmd(cmd='chassis power status',ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
        if power_status[0] == 0:
            if power_status[1] == 'Chassis Power is on':
                sys_status='on'
            elif power_status[1] == 'Chassis Power is off':
                sys_status='off'
            if (check_status and check_status == sys_status) or (check_status is None and sys_status in ['on','off']):
                if check_status:
                    logging("   * confirm state : {} => {}".format(sys_status,check_status),log_file=log_file,date=True,log=log,log_level=6)
                return [True,sys_status]
            else:
                if check_status:
                    logging("   - wait {}sec : {} => {}".format((wait_time - ii)*monitor_time,sys_status,check_status),log_file=log_file,date=True,log=log,log_level=6)
        else:
            logging("   - wait {}sec for check power state with {}:{}".format(monitor_time,ipmi_user,ipmi_pass),log_file=log_file,date=True,log=log,log_level=6)
        sleep(monitor_time)
    return [False,'time out']

def get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=None,log=None):
    status='No override'
    rc=ipmi_cmd(cmd='chassis bootparam get 5',ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
    if rc[0] == 0:
        efi=False
        persistent=False
        for ii in rc[1].split('\n'):
            if 'Options apply to all future boots' in ii:
                persistent=True
            elif 'BIOS EFI boot' in ii:
                efi=True
            elif 'Boot Device Selector :' in ii:
                status=ii.split(':')[1]
                break
        if log:
            log("Boot mode Status:{}, EFI:{}, Persistent:{}".format(status,efi,persistent),log_level=7)
        return [status,efi,persistent]
    else:
        return [False,False,False]

def set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,ipxe=False,persistent=False,log_file=None,log=None,force=False):
    boot_mode_d=['pxe','ipxe','bios','hdd']
    if not boot_mode in boot_mode_d:
        return
    if persistent:
        if boot_mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
            # ipmitool -I lanplus -H 172.16.105.74 -U ADMIN -P 'ADMIN' raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00
            ipmi_cmd(cmd='raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00',ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
            logging("Persistently Boot mode set to i{0} at {1}".format(boot_mode,ipmi_ip),log_file=log_file,date=True,log=log,log_level=7)
        else:
            ipmi_cmd(cmd='chassis bootdev {0} options=persistent'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
            logging("Persistently Boot mode set to {0} at {1}".format(boot_mode,ipmi_ip),log_file=log_file,date=True,log=log,log_level=7)
    else:
        if boot_mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                ipmi_cmd(cmd='chassis bootdev {0} options=efiboot'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
        else:
            if force and boot_mode == 'pxe':
                ipmi_cmd(cmd='chassis bootparam set bootflag force_pxe'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
            else:
                ipmi_cmd(cmd='chassis bootdev {0}'.format(boot_mode),ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
        logging("Temporary Boot mode set to {0} at {1}".format(boot_mode,ipmi_ip),log_file=log_file,date=True,log=log,log_level=7)


def do_power(ipmi_ip,ipmi_user,ipmi_pass,mode,num=2,log_file=None,log=None):
    power_mode={'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'cycle':['chassis power cycle']}
    if not mode in power_mode:
        return [False,'Unknown power mode']
    power_step=len(power_mode[mode])-1
    for ii in range(1,int(num)+1):
        logging("Power {} at {} (try:{}/{})".format(mode,ipmi_ip,ii,num),log_file=log_file,date=True,log=log,log_level=6)
        for rr in list(power_mode[mode]):
            verify_status=rr.split(' ')[-1]
            if verify_status in ['reset','cycle']:
                 sys_status=power_state(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
                 if sys_status[0] and sys_status[1] == 'off':
                     logging(" ! can not {} the power at {} status".format(verify_status,sys_status[1]),log_file=log_file,date=True,log=log,log_level=3)
                     return [False,'can not {} at {} status'.format(verify_status,sys_status[1])]
            rc=ipmi_cmd(cmd=rr,ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,log=log)
            if rc[0] == 0:
                logging(" + Do power {}".format(verify_status),log_file=log_file,date=True,log=log,log_level=5)
                if verify_status in ['reset','cycle']:
                    verify_status='on'
                    sleep(10)
            else:
                logging(" ! power {} fail".format(verify_status),log_file=log_file,date=True,log=log,log_level=3)
                break
            sys_status=power_state(ipmi_ip,ipmi_user,ipmi_pass,check_status=verify_status,log_file=log_file,log=log)
            if sys_status[0]:
                if sys_status[1] == verify_status:
                    if power_step == power_mode[mode].index(rr):
                        return sys_status + [ii]
                sleep(5)
            else:
                break
        sleep(3)
    return [False,'time out',ii]

def power_handle(ipmi_ip,mode='status',num=2,ipmi_user='ADMIN',ipmi_pass='ADMIN',boot_mode=None,order=False,ipxe=False,log_file=None,log=None,force=False):
    # Power handle
    if mode == 'status':
        return power_state(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
    if boot_mode:
        if ipxe in ['on','On',True,'True']:
            ipxe=True
        else:
            ipxe=False
        if boot_mode == 'ipxe':
            ipxe=True
            boot_mode='pxe'
        for ii in range(0,5):
            aa=set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,persistent=order,ipxe=ipxe,log_file=log_file,log=log,force=force)
            boot_mode_state=get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
            if (boot_mode == 'pxe' and boot_mode_state[0] is not False and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
                break
            logging(" retry boot mode set {} (ipxe:{},force:{})[{}/5]".format(boot_mode,ipxe,order,ii),log_file=log_file,date=True,log=log,log_level=3)
            time.sleep(2)
    rc=do_power(ipmi_ip,ipmi_user,ipmi_pass,mode,num=num,log_file=log_file,log=log)
#    if ipxe in ['on','On',True,'True']:
#        ipxe=True
#    if rc[0]:
#        if boot_mode:
#            for ii in range(0,5):
#                set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,persistent=order,ipxe=ipxe,log_file=log_file,log=log)
#                boot_mode_state=get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
#                if (boot_mode == 'pxe' and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
#                    break
#                logging(" retry boot mode set {} (ipxe:{},force:{})[{}/5]".format(boot_mode,ipxe,order,ii),log_file=log_file,date=True,log=log)
#                time.sleep(2)
    return rc

def wait_ready_system(ipmi_ip,ipmi_user='ADMIN',ipmi_pass='ADMIN',timeout=1800,keep_up=45,down_monitor=300,interval=3,stop_func=None,stop_arg={},log_file=None,log=None):
    aa="""ipmitool -I lanplus -H {0} -U {1} -P {2} sdr type Temperature 2>/dev/null""".format(ipmi_ip,ipmi_user,ipmi_pass)
    chk=0
    if keep_up >= timeout:
       timeout=int('{}'.format(keep_up)) + 30
    if down_monitor >= timeout:
       timeout=int('{}'.format(down_monitor)) + 30
    log_type=type(log).__name__
    init_sec=int(datetime.now().strftime('%s'))
    do_sec=int('{}'.format(init_sec))
    wait_count=0
    count_down=(down_monitor//interval)
    max_wait=keep_up//interval
    node_state=None
    node_old=None
    node_change=False
    node_change_count=0

    if count_down > 0:
        logging("Wait until the system({}) is ready(keep {}sec)".format(ipmi_ip,keep_up),log_file=log_file,date=True,log=log,log_level=6)
    else:
        logging("Wait until the system({}) is ready(keep {}sec) after down(check time: {} sec)".format(ipmi_ip,keep_up,down_monitor),log_file=log_file,date=True,log=log,log_level=6)
    while True:
        if stop_func and type(stop_arg) is dict:
            if stop_func(**stop_arg) is True:
                if log_type=='function':
                    logging("Got STOP signal",log_file=log_file,date=True,log=log,log_level=3)
#                    log("Got STOP signal",log_level=6)
                return [False,'Got STOP signal']
        if do_sec - init_sec > timeout and node_state == node_old:
            if log_type=='function':
                logging("TIme Out, node state is {}".format(node_state),log_file=log_file,date=True,log=log,log_level=3)
#                log("Time Out, node state is {}".format(node_state),log_level=6)
            return [False,'Time Out, node state is {}'.format(node_state)]
        if ping(ipmi_ip,2):
            tempc=[]
            wrc=rshell(aa)
            if wrc[0] == 0:
                 for ii in wrc[1].split('\n'):
                      if re.findall('CPU?[0-9]?.Temp',ii) or re.findall('System.Temp',ii):
                          tempc=re.findall('(\d+) degrees',ii.split('|')[-1])
                          if tempc:
                              break
                 if tempc and int(tempc[0]) > 0:
                     node_state='up'
                 else:
                     node_state='down'
                 if node_state and node_old and node_state != node_old:
                     if node_change_count < 4:
                         init_sec=int(datetime.now().strftime('%s'))
                     wait_count=0
                     count_down=(down_monitor//interval)
                     node_change=True 
                     node_change_count=node_change_count+1
                 if (down_monitor == 0 or node_change) and node_state == 'up':
                     wait_count=wait_count+1
                     if wait_count > max_wait:
                         logging("System ready",log_file=log_file,date=True,log=log,log_level=6)
                         #if log_type=='function':
                         #    log("The system ready",log_level=6)
                         return [True,'System ready']
                 elif down_monitor > 0 and node_change is False and node_state in ['up','down']:
                     count_down=count_down-1
                     if count_down < 0:
                         logging("It did not changed state. still {}".format(node_state),log_file=log_file,date=True,log=log,log_level=3)
                         #if log_type=='function':
                         #    log("It did not changed state. still {}".format(node_state),log_level=6)
                         return [False,'It did not changed state. still {}'.format(node_state)]
                 if chk % 5 == 0:
                     if node_state != node_old:
                         mark='+'
                     else:
                         mark='-'
                     if count_down > 0:
                         logging(" {2} wait {1}sec for ready system({3}:{4}) at {0}".format(ipmi_ip, (timeout - (do_sec - init_sec)),mark,ipmi_user,ipmi_pass),log_file=log_file,date=True,log=log,log_level=6)
                     else:
                         logging(" {2} wait {1}sec for ready system({3}:{4}) at {0} after down".format(ipmi_ip, (timeout - (do_sec - init_sec)),mark,ipmi_user,ipmi_pass),log_file=log_file,date=True,log=log,log_level=6)
                 node_old='{}'.format(node_state)
            else:
                if chk % 5 == 0:
                    if count_down > 0:
                        logging("Wait {1}sec for readable sensor data from the system({2}:{3}) at {0}".format(ipmi_ip, (timeout - (do_sec - init_sec)),ipmi_user,ipmi_pass),log_file=log_file,date=True,log=log,log_level=6)
                    else:
                        logging("Wait {1}sec for readable sensor data from the system({2}:{3}) at {0} after down".format(ipmi_ip, (timeout - (do_sec - init_sec)),ipmi_user,ipmi_pass),log_file=log_file,date=True,log=log,log_level=6)
        else:
            if chk % 5 == 0:
                logging(" - can't ping to {0}".format(ipmi_ip),log_file=log_file,date=True,log=log,log_level=3)
        chk=chk+1
        sleep(interval)
        do_sec=int(datetime.now().strftime('%s'))
    if log_type=='function':
        logging("Unknown status",log_file=log_file,date=True,log=log,log_level=6)
#        log("Unknown status",log_level=6)
    return [None,'Unknown status']

#def get_lanmode(smcipmitool_file,smcipmitool_opt):
#    if smcipmitool_file is not None and smcipmitool_opt is not None:
#        lanmode_info=rshell('''java -jar {0}/{1} {2}'''.format(tool_path,os.path.basename(smcipmitool_file),smcipmitool_opt))
#        if lanmode_info[0] == 144:
#            a=re.compile('Current LAN interface is \[ (\w.*) \]').findall(lanmode_info[1])
#            if len(a) == 1:
#                return a[0]
#    return

def sizeConvert(sz=None,unit='b:g'):
    if sz is None:
        return False
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
            sz=inc(sz)
        else:
            sz=dec(sz)
    return sz

def git_ver(git_dir=None):
    if git_dir is not None and os.path.isdir('{0}/.git'.format(git_dir)):
        gver=rshell('''cd {0} && git describe --tags'''.format(git_dir))
        if gver[0] == 0:
            return gver[1]
#        branch=rshell('''cd {0} && git branch| head -1'''.format(git_dir))
#        tag=rshell('''cd {0} && git tag|tail -1'''.format(git_dir))
#        if branch[0] == 0:
#            if branch[1].split(' ')[1] == 'master':
#                return gver[1]
#            else:
#                return gver[1].replace(tag[1],'v{0}'.format(branch[1].split(' ')[1]))
    return

def load_kmod(modules=[]):
    if type(modules) is list:
        for ii in modules:
            os.system('lsmod | grep {0} >& /dev/null && modprobe -r {1}; modprobe --ignore-install {1} || modprobe {1}'.format(ii.split('-')[0],ii))
            #os.system('lsmod | grep {0} >& /dev/null || modprobe -i -f {1}'.format(ii.split('-')[0],ii))
        return
    print('modules is not list type data ({0})'.format(modules))
    return False

def reduce_string(string,symbol=' ',snum=0,enum=None):
    if type(string) is str:
        arr=string.split(symbol)
    strs=None
    if enum is None:
        enum=len(arr)
    for ii in range(snum,enum):
        if strs is None:
            strs='{0}'.format(arr[ii])
        else:
            strs='{0} {1}'.format(strs,arr[ii])
    return strs

def list2str(arr):
    rc=None
    for i in arr:
        if rc:
            rc='{0} {1}'.format(rc,i)
        else:
            rc='{0}'.format(i)
    return rc


def findstr(string,find,prs=None,split_symbol='\n',patern=True):
    # Patern return selection (^: First(0), $: End(-1), <int>: found item index)
    found=[]
    if type(string) is not str:
        return found
    if split_symbol:
        string_a=string.split(split_symbol)
    else:
        string_a=[string]
    for nn in string_a:
        if type(find) in [list,tuple]:
            find=list(find)
        else:
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

def find_cdrom_dev():
    if os.path.isdir('/sys/block') is False:
        return
    for r, d, f in os.walk('/sys/block'):
        for dd in d:
            for rrr,ddd,fff in os.walk(os.path.join(r,dd)):
                if 'removable' in fff:
                    with open('{0}/removable'.format(rrr),'r') as fp:
                        removable=fp.read()
                    if '1' in removable:
                        if os.path.isfile('{0}/device/model'.format(rrr)):
                            with open('{0}/device/model'.format(rrr),'r') as fpp:
                                model=fpp.read()
                            for ii in ['CDROM','DVD-ROM','DVD-RW']:
                                if ii in model:
                                    return '/dev/{0}'.format(dd)

#def ipmi_sol(ipmi_ip,ipmi_user,ipmi_pass):
#    if is_ipv4(ipmi_ip):
#        rshell('''ipmitool -I lanplus -H {} -U {} -P {} sol info'''.format(ipmi_ip,ipmi_user,ipmi_pass))
#Set in progress                 : set-complete
#Enabled                         : true
#Force Encryption                : false
#Force Authentication            : false
#Privilege Level                 : OPERATOR
#Character Accumulate Level (ms) : 0
#Character Send Threshold        : 0
#Retry Count                     : 0
#Retry Interval (ms)             : 0
#Volatile Bit Rate (kbps)        : 115.2
#Non-Volatile Bit Rate (kbps)    : 115.2
#Payload Channel                 : 1 (0x01)
#Payload Port                    : 623

def _u_str2int(val,encode='utf-8'):
    if sys.version_info > (3,0):
        if type(val) is bytes:
            return int(val.hex(),16)
        else:
            return int(_u_bytes(val,encode=encode).hex(),16)
    return int(val.encode('hex'),16)

def _u_bytes(val,encode='utf-8'):
    if sys.version_info > (3,0):
        if type(val) is bytes:
            return val
        else:
            return bytes(val,encode)
    return bytes(val)

#def _u_byte2str(val,encode='windows-1252'):
def _u_byte2str(val,encode='latin1'):
    return val.decode(encode)

def net_send_data(sock,data,key='kg',enc=False,timeout=0):
    if type(sock).__name__ in ['socket','_socketobject'] and data and type(key) is str and len(key) > 0 and len(key) < 7:
        # encode code here
        if timeout > 0:
            sock.settimeout(timeout)
        nkey=_u_str2int(key)
        pdata=pickle.dumps(data,protocol=2) # common 2.x & 3.x version : protocol=2
        data_type=_u_bytes(type(data).__name__[0])
        if enc and key:
            # encode code here
            #enc_tf=_u_bytes('t') # Now not code here. So, everything to 'f'
            #pdata=encode(key,pdata)
            enc_tf=_u_bytes('f')
        else:
            enc_tf=_u_bytes('f')
        ndata=struct.pack('>IssI',len(pdata),data_type,enc_tf,nkey)+pdata
        try:
            sock.sendall(ndata)
            return True
        except:
            pass
    return False

def _dict(pk={},add=False,**var):
    for key in var.keys():
        if key in pk:
            pk.update({key:var[key]})
        else:
            if add:
                pk[key]=var[key]
            else:
                return False
    return pk

def net_receive_data(sock,key='kg',progress=None):
    # decode code here
    def recvall(sock,count): # Packet
        buf = b''
        file_size_d=int('{0}'.format(count))
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
            if progress is not None:
                sys.stdout.write("%s: [%3.1f%%]\r" %(progress,(1 - count/file_size_d) * 100.))
                sys.stdout.flush()
        if progress is not None:
            print('')
        return buf
    head=recvall(sock,10)
    if head:
        try:
            st_head=struct.unpack('>IssI',_u_bytes(head))
        except:
            return [False,'Fail for read header({})'.format(head)]
        if st_head[3] == _u_str2int(key):
            data=recvall(sock,st_head[0])
            if data:
                if st_head[2] == 't':
                    # decode code here
                    # data=decode(data)
                    pass
                return [st_head[1],pickle.loads(data)]
            return [True,None]
        else:
            return [False,'Wrong key']
    return [False,'Wrong packet({})'.format(head)]

def net_put_and_get_data(IP,data,PORT=8805,key='kg',timeout=3,try_num=1,try_wait=[0,5],progress=None,enc=False,upacket=None):
    for ii in range(0,try_num):
        if upacket: # Update packet function for number of try information ([#/<total #>])
            data=upacket('ntry',[ii+1,try_num],data)
        sock=net_get_socket(IP,PORT,timeout=timeout)
        sent=False
        try:
            sent=net_send_data(sock,data,key=key,enc=enc)
        except:
            print('send fail, try again ... [{}/{}]'.format(ii+1,try_num))
        if sent:
            try:
                return net_receive_data(sock,key=key,progress=progress)
            except:
                return [False,'Data protocol version mismatch']
        if sock:
            sock.close()
        if try_num > 1:
            print('try send data ... [{}/{}]'.format(ii+1,try_num))
            sleep(try_wait)
    return [False,'Send fail :\n%s'%(data)]

def net_get_socket(host,port,timeout=3,dbg=0): # host : Host name or IP
    try:
        af, socktype, proto, canonname, sa = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)[0]
    except:
        print('Can not get network informatin of {}:{}'.format(host,port))
        return False
    try:
        soc = socket.socket(af, socktype, proto)
        if timeout > 0:
            soc.settimeout(timeout)
    except socket.error as msg:
        print('could not open socket of {0}:{1}\n{2}'.format(host,port,msg))
        return False
    try:
        soc.connect(sa)
        return soc
    except socket.error as msg:
        if dbg > 3:
            print('can not connect at {0}:{1}\n{2}'.format(host,port,msg))
        return False

def net_start_server(server_port,main_func_name,server_ip='',timeout=0,max_connection=10,log_file=None):
    ssoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if timeout > 0:
        ssoc.settimeout(timeout)
    try:
        ssoc.bind((server_ip, server_port))
    except socket.error as msg:
        print('Bind failed. Error : {0}'.format(msg))
        os._exit(1)
    ssoc.listen(max_connection)
    print('Start server for {0}:{1}'.format(server_ip,server_port))
    # for handling task in separate jobs we need threading
    while True:
        conn, addr = ssoc.accept()
        ip, port = str(addr[0]), str(addr[1])
        try:
            Thread(target=main_func_name, args=(conn, ip, port, log_file)).start()
        except:
            print('No more generate thread for client from {0}:{1}'.format(ip,port))
    ssoc.close()

def net_start_single_server(server_port,main_func_name,server_ip='',timeout=0,max_connection=10,log_file=None):
    ssoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if timeout > 0:
        ssoc.settimeout(timeout)
    try:
        ssoc.bind((server_ip, server_port))
    except socket.error as msg:
        print('Bind failed. Error : {0}'.format(msg))
        os._exit(1)
    ssoc.listen(max_connection)
    print('Start server for {0}:{1}'.format(server_ip,server_port))
    # for handling task in separate jobs we need threading
    conn, addr = ssoc.accept()
    ip, port = str(addr[0]), str(addr[1])
    rc=main_func_name(conn, ip, port, log_file)
    ssoc.close()
    return rc

def sleep(try_wait=None):
    try_wait_type=type(try_wait)
    if try_wait in [None,True]:
        time.sleep(1)
    elif try_wait_type is list:
        if len(try_wait) == 2:
            try:
                time.sleep(random.randint(int(try_wait[0]),int(try_wait[1])))
            except:
                time.sleep(1)
        else:
            try:
                time.sleep(int(try_wait[0]))
            except:
                time.sleep(1)
    elif try_wait_type is str:
        if try_wait.isdigit():
            time.sleep(int(try_wait))
    else:
        try:
            time.sleep(try_wait)
        except:
            time.sleep(1)

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

def file_mode(val):
    val_type=type(val)
    if val_type is int:
        if val > 511:
            return oct(val)[-4:]
        elif val > 63:
            return oct(val)
    elif val_type is str:
        cnt=len(val)
        num=int(val)
        if cnt >=3 and cnt <=4 and num >= 100 and num <= 777:
            return int(val,8)

def get_file(filename,**opts):
    md5sum=opts.get('md5sum',False)
    data=opts.get('data',False)
    include_dir=opts.get('include_dir',False)
    include_sub_dir=opts.get('include_sub_dir',False)

    def get_file_data(filename,root_path=None):
        rc={'name':os.path.basename(filename),'path':os.path.dirname(filename),'exist':False,'dir':False,'link':False}
        if root_path:
            in_filename=os.path.join(root_path,filename)
        else:
            in_filename=filename
        if os.path.exists(in_filename):
            fstat=os.stat(in_filename)
            rc['uid']=fstat.st_uid
            rc['gid']=fstat.st_gid
            rc['size']=fstat.st_size
            rc['atime']=fstat.st_atime
            rc['mtime']=fstat.st_mtime
            rc['ctime']=fstat.st_ctime
            rc['inod']=fstat.st_ino
            rc['mode']=oct(fstat.st_mode)[-4:]
            rc['exist']=True
            if os.path.islink(in_filename):
                rc['link']=True
            else:
                rc['link']=False
                if os.path.isdir(in_filename):
                    rc['dir']=True
                    rc['path']=in_filename
                    rc['name']=''
                else:
                    rc['dir']=False
                    if md5sum or data:
                        with open(in_filename,'rb') as f:
                            fdata=f.read()
                        if md5sum:
                            rc['md5']=md5(fdata)
                        if data:
                            rc['data']=fdata
        return rc

    rc={'exist':False,'includes':[]}
    rc.update(get_file_data(filename))
    if rc['dir']:
        root_path=filename
        real_filename=None
    else:
        root_path=os.path.dirname(filename)
        real_filename=os.path.basename(filename)
    if include_dir:
        for dirPath, subDirs, fileList in os.walk(root_path):
            curDir=os.path.join(dirPath.lstrip('{}/'.format(root_path)))
            for sfile in fileList:
                curFile=os.path.join(curDir,sfile)
                if curFile != real_filename:
                    rc['includes'].append(get_file_data(curFile,root_path))
            if include_sub_dir is False:
                break
    return rc
        

def get_node_info():
    return {
         'host_name':get_host_name(),
         'host_ip':get_host_ip(),
         'host_mac':get_host_mac(),
         'ipmi_ip':get_ipmi_ip()[1],
         'ipmi_mac':get_ipmi_mac()[1],
         }

def int_sec():
    return int(datetime.now().strftime('%s'))

def now():
    return int_sec()

def timeout(timeout_sec,init_time=None,default=(24*3600)):
    if type(timeout_sec) is not int:
        timeout_sec=default
        if timeout_sec < 3:
           timeout_sec=3
    if type(init_time) is not int:
        init_time=int_sec()
    if int_sec() - init_time >  timeout_sec:
        return True,init_time
    return False,init_time

def kmp(mp={},func=None,name=None,timeout=0,quit=False,log_file=None,log_screen=True,log_raw=False, argv=[],queue=None):
    # Clean
    for n in mp:
        if quit is True:
            if n != 'log':
                mp[n]['mp'].terminate()
                if 'log' in mp:
                    mp['log']['queue'].put('\nterminate function {}'.format(n))
        else:
            if mp[n]['timeout'] > 0 and int_sec() > mp[n]['timeout']:
                mp[n]['mp'].terminate()
                if 'log' in mp:
                    mp['log']['queue'].put('\ntimeout function {}'.format(n))
        if not mp[n]['mp'].is_alive():
            del mp[n]
    if quit is True and 'log' in mp:
        mp['log']['queue'].put('\nterminate function log')
        time.sleep(1)
        mp['log']['mp'].terminate()
        return

    # LOG
    def logging(ql,log_file=None,log_screen=True,raw=False):
        while True:
            #if not ql.empty():
            if ql.empty():
                time.sleep(0.01)
            else:
                ll=ql.get()
                if raw:
                    log_msg=ll
                else:
                    log_msg='{} : {}\n'.format(datetime.now().strftime('%m-%d-%Y %H:%M:%S'),ll)
                if type(log_msg) is not str:
                    log_msg='{}'.format(log_msg)
                if log_file and os.path.isdir(os.path.dirname(log_file)):
                    with open(log_file,'a') as f:
                        f.write('{}'.format(log_msg))
                if log_screen:
                    sys.stdout.write(log_msg)
                    sys.stdout.flush()

    if 'log' not in mp or not mp['log']['mp'].is_alive():
        log=multiprocessing.Queue()
        lqp=multiprocessing.Process(name='log',target=logging,args=(log,log_file,log_screen,log_raw,))
        lqp.daemon = True
        mp.update({'log':{'mp':lqp,'start':int_sec(),'timeout':0,'queue':log}})
        lqp.start()

    # Functions
    if func:
        if name is None:
            name=func.__name__
        if name not in mp:
            if argv:
                mf=multiprocessing.Process(name=name,target=func,args=tuple(argv))
            else:
                mf=multiprocessing.Process(name=name,target=func)
            if timeout > 0:
                timeout=int_sec()+timeout
            
#            for aa in argv:
#                if type(aa).__name__ == 'Queue':
#                    mp.update({name:{'mp':mf,'timeout':timeout,'start':now(),'queue':aa}})
            if name not in mp:
                if queue and type(queue).__name__ == 'Queue':
                    mp.update({name:{'mp':mf,'timeout':timeout,'start':int_sec(),'queue':queue}})
                else:
                    mp.update({name:{'mp':mf,'timeout':timeout,'start':int_sec()}})
            mf.start()
    return mp

def net_put_data(IP,data,PORT=8805,key='kg',timeout=3,try_num=1,try_wait=[1,10],progress=None,enc=False,upacket=None,dbg=0,wait_time=3):
    for ii in range(0,try_num):
        if upacket: # Update packet function for number of try information ([#/<total #>])
            data=upacket('ntry',[ii+1,try_num],data)
        sock=net_get_socket(IP,PORT,timeout=timeout,dbg=dbg)
        if sock is False:
            if dbg >= 3:
                print('Can not get socket data [{}/{}], wait {}s'.format(ii+1,try_num,wait_time))
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(wait_time)
            continue
        sent=False
        try:
            sent=net_send_data(sock,data,key=key,enc=enc)
        except:
            print('send fail, try again ... [{}/{}]'.format(ii+1,try_num))
        if sent:
            if sock:
                sock.close()
            return [True,'sent']
        if try_num > 1:
            wait_time=make_second(try_wait)
            if dbg >= 3:
                print('try send data ... [{}/{}], wait {}s'.format(ii+1,try_num,wait_time))
            time.sleep(wait_time)
    return [False,'Send fail :\n%s'%(data)]


def make_second(try_wait=None):
    wait_time=1
    try_wait_type=type(try_wait)
    if try_wait in [None,True]:
        time.sleep(wait_time)
    if try_wait_type is list:
        if len(try_wait) == 2:
            wait_time=random.randint(int(try_wait[0]),int(try_wait[1]))
        else:
            wait_time=int(try_wait[0])
    elif try_wait_type is str:
        if try_wait.isdigit():
            wait_time=int(try_wait)
    elif try_wait_type is int:
        wait_time=try_wait
    return wait_time

def web_server_ip(request):
    return request.get_host().split(':')

def web_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def web_req(host_url,**opts):
    # remove SSL waring error message (test)
    requests.packages.urllib3.disable_warnings() 

    mode=opts.get('mode','get')
    max_try=opts.get('max_try',3)
    auth=opts.get('auth',None)
    user=opts.get('user',None)
    ip=opts.get('ip',None)
    port=opts.get('port',None)
    passwd=opts.get('passwd',None)
    timeout=opts.get('timeout',None)
    https=opts.get('https',False)
    verify=opts.get('verify',True)
    request_url=opts.get('request_url',None)
    log=opts.get('log',None)
    log_level=opts.get('log_level',8)
    logfile=opts.get('logfile',None)
    if https:
        verify=False
    if auth is None and user and passwd:
        if type(user) is not str or type(passwd) is not str:
            printf("user='<user>',passwd='<pass>' : format(each string)",dsp='e',log=log,log_level=log_level,logfile=logfile)
            return False,"user='<user>',passwd='<pass>' : format(each string)"
        auth=(user,passwd)
    if auth and type(auth) is not tuple:
        printf("auth=('<user>','<pass>') : format(tuple)",dsp='e',log=log,log_level=log_level,logfile=logfile)
        return False,"auth=('<user>','<pass>') : format(tuple)"
    data=opts.get('data',None) # dictionary format
    if data and type(data) is not dict:
        printf("data={'<key>':'<val>',...} : format(dict)",dsp='e',log=log,log_level=log_level,logfile=logfile)
        return False,"data={'<key>':'<val>',...} : format(dict)"
    files=opts.get('files',None) # dictionary format
    if files and type(files) is not dict:
        printf("files = { '<file parameter name>': (<filename>, open(<filename>,'rb'))} : format(dict)",dsp='e',log=log,log_level=log_level,logfile=logfile)
        return False,"files = { '<file parameter name>': (<filename>, open(<filename>,'rb'))} : format(dict)"
    if type(host_url) is str:
        if host_url.find('https://') == 0:
            verify=False
    elif ip:
        if verify:
            host_url='http://{}'.format(ip)
        else:
            host_url='https://{}'.format(ip)
        if port:
            host_url='{}:{}'.format(host_url,port)
        if request_url:
            host_url='{}/{}'.format(host_url,request_url)
    else:
        return False,'host_url or ip not found'    
    ss = requests.Session()
    for j in range(0,max_try):
        try:
            if mode == 'post':
                r =ss.post(host_url,verify=verify,auth=auth,data=data,files=files,timeout=timeout)
            else:
                r =ss.get(host_url,verify=verify,auth=auth,data=data,files=files,timeout=timeout)
            return True,r
        except requests.exceptions.RequestException as e:
            host_url_a=host_url.split('/')[2]
            server_a=host_url_a.split(':')
            if len(server_a) == 1:
                printf("Server({}) has no response (wait {}/{} (10s))".format(server_a[0],j,max_try),dsp='e',log=log,log_level=log_level,logfile=logfile)
            else:
                printf("Server({}:{}) has no response (wait {}/{} (10s))".format(server_a[0],server_a[1],j,max_try),dsp='e',log=log,log_level=log_level,logfile=logfile)
        time.sleep(10)
    return False,'TimeOut'

def remove_end_new_line(data,new_line='\n'):
    if type(data) is str:
        data_a=data.split(new_line)
        if data_a[-1] == '':
            del data_a[-1]
        return '\n'.join(data_a)
    return data

def screen_logging(title,cmd):
    # ipmitool -I lanplus -H 172.16.114.80 -U ADMIN -P ADMIN sol activate
    tmp_file=mktemp('/tmp/.slc.cfg')
    log_file=mktemp('/tmp/.screen_ck_{}.log'.format(title))
    if os.path.isfile(log_file):
        log_file=''
    with open(tmp_file,'w') as f:
        f.write('''logfile {}\nlogfile flush 0\nlog on\n'''.format(log_file))
    if os.path.isfile(tmp_file):
        rc=rshell('''screen -c {} -dmSL "{}" {}'''.format(tmp_file,title,cmd))
        if rc[0] == 0:
            for ii in range(0,50):
                if os.path.isfile(log_file):
                    os.unlink(tmp_file)
                    return log_file
                time.sleep(0.1)

def screen_id(title=None):
    scs=[]
    rc=rshell('''screen -ls''')
    if rc[0] == 1:
        for ii in rc[1].split('\n')[1:]:
            jj=ii.split()
            if len(jj) == 2:
                if title:
                    zz=jj[0].split('.')
                    if zz[1] == title:
                        scs.append(jj[0])
                else:
                    scs.append(jj[0])
    return scs

def screen_kill(title):
    ids=screen_id(title)
    if len(ids) == 1:
        rc=rshell('''screen -X -S {} quit'''.format(ids[0]))
        if rc[0] == 0:
            return True
        return False

def screen_monitor(title,cmd,find=[],timeout=600):
    # Linux OS Boot (Completely kernel loaded): find=['initrd0.img','\xff']
    # PXE Boot prompt: find=['boot:']
    # PXE initial : find=['PXE ']
    # DHCP initial : find=['DHCP'] 
    # ex: aa=screen_monitor('test','ipmitool -I lanplus -H <bmc ip> -U ADMIN -P ADMIN sol activate',find=['initrd0.img','\xff'],timeout=300)
    log_file=screen_logging(title,cmd)
    init_time=int_sec()
    if log_file:
        mon_line=0
        old_mon_line=-1
        found=0
        find_num=len(find)
        while True:
            if int_sec() - init_time > timeout :
                print('Monitoring timeout({} sec)'.format(timeout))
                if screen_kill(title):
                    os.unlink(log_file)
                break
            with open(log_file,'rb') as f:
                tmp=f.read()
            if type(tmp) is bytes:
                tmp=_u_byte2str(tmp)
            if '\x1b' in tmp:
                tmp_a=tmp.split('\x1b')
            elif '\r\n' in tmp:
                tmp_a=tmp.split('\r\n')
            elif '\r' in tmp:
                tmp_a=tmp.split('\r')
            else:
                tmp_a=tmp.split('\n')
            tmp_n=len(tmp_a)
            for ii in tmp_a[mon_line:]:
                if find_num == 0:
                    print(ii)
                else:
                    for ff in range(0,find_num):
                        find_i=find[found]
                        if ii.find(find_i) < 0:
                            break
                        found=found+1
                        if found >= find_num:
                            if screen_kill(title):
                                os.unlink(log_file)
                            return True
            if tmp_n > 1:
                mon_line=tmp_n -1
            else:
                mon_line=tmp_n
            time.sleep(1)
    return False

def value_check(src,val,key=None):
    type_src=type(src)
    if type_src is list:
        len_src=len(src)
        if key is None:
            if val in src:
                return True
        else:
            if type(key) in [str,int]:
                key=int(key)
                if len_src > key:
                    if src[key] == val:
                        return True
    elif type_src is dict:
        if key is None:
            for ii in src:
                if val == src[ii]:
                    return True
        else:
            if key in src and val == src[key]:
                return True
    elif type_src is str:
        if key is None:
            if val in src:
                return True
        else:
            if type(key) is int:
                if key < 0:
                    if val == src[key-len(val):]:
                         return True
                elif key == 0:
                    if val == src[:len(val)]:
                         return True
                else:
                    if val == src[key:key+len(val)]:
                         return True
    return False

def check_value(val,pool):
    type_pool=type(pool)
    if type_pool is dict:
        pool=list(pool.keys())
        type_pool=list
    if type_pool in [list,tuple]:
        for ii in pool:
            if isinstance(ii,bool):
                if isinstance(val,bool) and ii == val:
                    return True
            else:
                if ii == val:
                    return True
    return False

def get_value(src,key=None,default=None):
    type_src=type(src)
    type_key=type(key)
    if type_src is bool:
        return src
    elif type_src is int:
        return src
    if key is None:
        return default
    if type_src in [str,list,tuple]:
        if type_key in [list,tuple]:
            rc=[]
            for kk in key:
                if type(kk) in int and len(src) > kk:
                    rc.append(src[kk])
                else:
                    rc.append(default)
            if type_key is tuple:
                return tuple(rc)
            return tuple(rc)
        else:
            if type(key) is int and len(src) > key:
                return src[key]
    elif type_src is dict:
        if type_key in [list,tuple]:
            rc=[]
            for kk in key:
                rc.append(src.get(kk,default))
            if type_key is tuple:
                return tuple(rc)
            return rc
        return src.get(key,default)
    elif type_src.__name__ in ['instance','classobj']:
        if type_key in [list,tuple]:
            for kk in key:
                rc.append(getattr(src,kk,default))
            if type_key is tuple:
                return tuple(rc)
        return getattr(src,key,default)
    return default

def encode(string):
    enc='{0}'.format(string)
    tmp=zlib.compress(enc.encode("utf-8"))
    return '{0}'.format(base64.b64encode(tmp).decode('utf-8'))

def decode(string):
    if type(string) is str:
        dd=zlib.decompress(base64.b64decode(string))
        return '{0}'.format(dd.decode("utf-8"))
    return string

def string2data(string):
    try:
        return ast.literal_eval(string)
    except:
        return string

def mount_samba(url,user,passwd,mount_point):
    if os.path.isdir(mount_point) is False:
        os.system('sudo mkdir -p {0}'.format(mount_point))
        time.sleep(1)
    if os.path.isdir(mount_point) is False:
        return False,'can not make a {} directory'.format(mount_point),'can not make a {} directory'.format(mount_point),0,0,None,None
    if 'smb://' in url:
        url_a=url.split('/')
        url_m=len(url_a)
        iso_file=url_a[-1]
        new_url=''
        for i in url_a[2:url_m-1]:
            new_url='{0}/{1}'.format(new_url,i)
        return rshell('''sudo mount -t cifs -o user={0} -o password={1} /{2} {3}'''.format(user,passwd,new_url,mount_point))
    else:
        url_a=url.split('\\')
        url_m=len(url_a)
        iso_file=url_a[-1]
        new_url=''
        for i in url_a[1:url_m-1]:
            new_url='{0}/{1}'.format(new_url,i)
        return km.rshell('''sudo mount -t cifs -o user={0} -o password={1} {2} {3}'''.format(user,passwd,new_url,mount_point))

def unmount(mount_point,del_dir=False):
    rc=km.rshell('''[ -d {0} ] && sudo mountpoint {0} && sudo umount {0} && sleep 1'''.format(mount_point))
    if rc[0] == 0 and del_dir:
        os.system('[ -d {0} ] && rmdir {0}'.format(mount_point))
    return rc

if __name__ == "__main__":
    class ABC:
        uu=3
        def __init__(self):
            self.a=1
            self.b=2
    print(get_value(ABC(),'b',default=None))
    print(get_value(ABC(),'uu',default=None))
    print(get_value(ABC(),'ux',default=None))
