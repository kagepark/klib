# Kage Park
# Inteligent BMC Tool
# Version 2

import os
from distutils.spawn import find_executable
import time
import sys
import kmisc as km
import kDict
import json

class Ipmitool:
    def __init__(self,**opts):
        self.__name__='ipmitool'
        self.tool_path=None
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status'],'shutdown':['chassis power soft']})
        self.ipmitool=True
        if find_executable('ipmitool') is False:
            self.ipmitool=False

    def cmd_str(self,cmd,**opts):
        if not self.ipmitool:
            km.logging('Install ipmitool package(yum install ipmitool)'.format(self.smc_file),log=self.log,log_level=1,dsp='e')
            return False,'ipmitool file not found',{}
        cmd_a=cmd.split()
        option=opts.get('option','lanplus')
        if km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'power',1) and km.get_value(cmd_a,2) in self.power_mode:
            cmd_a[0] = 'chassis'
        elif km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'reset',1):
            cmd_a=['mc','reset','cold']
        elif km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'lan',1):
            if len(cmd_a) == 3 and cmd_a[2] in ['mac','dhcp','gateway','netmask']:
                cmd_a=['lan','print']
        elif km.check_value(cmd_a,'ipmi',0) and km.check_value(cmd_a,'sensor',1):
            cmd_a=['sdr','type','Temperature']
        return True,'''ipmitool -I %s -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' %s'''%(option,' '.join(cmd_a)),None,{'ok':[0],'fail':[1]},None


class Smcipmitool:
    def __init__(self,**opts):
        self.__name__='smc'
        self.tool_path=opts.get('tool_path',None)
        self.smc_file=None
        if self.tool_path and os.path.isdir(self.tool_path):
            self.smc_file='{}/{}'.format(self.tool_path,opts.get('smc_file',None))
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['ipmi power up'],'off':['ipmi power down'],'reset':['ipmi power reset'],'off_on':['ipmi power down','ipmi power up'],'on_off':['ipmi power up','ipmi power down'],'cycle':['ipmi power cycle'],'status':['ipmi power status'],'shutdown':['ipmi power softshutdown']})

    def cmd_str(self,cmd,**opts):
        cmd_a=cmd.split()
        if not self.smc_file:
            km.logging('- SMCIPMITool({}) not found'.format(self.smc_file),log=self.log,log_level=1,dsp='e')
            return False,'SMCIPMITool file not found',{}
        if km.check_value(cmd_a,'chassis',0) and km.check_value(cmd_a,'power',1):
            cmd_a[0] == 'ipmi'
        elif km.check_value(cmd_a,'mc',0) and km.check_value(cmd_a,'reset',1) and km.check_value(cmd_a,'cold',2):
            cmd_a=['ipmi','reset']
        elif km.check_value(cmd_a,'lan',0) and km.check_value(cmd_a,'print',1):
            cmd_a=['ipmi','lan','mac']
        elif km.check_value(cmd_a,'sdr',0) and km.check_value(cmd_a,'Temperature',2):
            cmd_a=['ipmi','sensor']
        return True,'''sudo java -jar %s {ipmi_ip} {ipmi_user} '{ipmi_pass}' %s'''%(self.smc_file,' '.join(cmd_a)),None,{'ok':[0,144],'error':[180],'err_bmc_user':[146],'err_connection':[145]},None

class Redfish:
    def __init__(self,**opts):
        self.__name__='redfish'
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status'],'shutdown':['chassis power soft']})

    def cmd_str(self,cmd,**opts):
        return True,'''https://{ipmi_ip}/redfish/v1/%s'''%(cmd),None,{'ok':[0,144],'error':[180],'err_bmc_user':[146],'err_connection':[145]},None

def move2first(item,pool):
    if item: 
        if type(pool) is list and item in pool:
            pool.remove(item)
        return [item]+pool
    return pool

class kBmc:
    def __init__(self,*inps,**opts):
        self.log=opts.get('log',None)
        if inps and type(inps[0]).__name__ == 'instance':
            self.root=inps[0].root
        else: 
            self.root=kDict.kDict()
            self.root.PUT('ipmi_port',opts.get('ipmi_port',623))
            ipmi_user=opts.get('ipmi_user','ADMIN')
            self.root.PUT('ipmi_user',ipmi_user)
            ipmi_pass=opts.get('ipmi_pass','ADMIN')
            self.root.PUT('ipmi_pass',ipmi_pass)
            test_user=opts.get('test_user',['ADMIN','Admin','admin','root','Administrator'])
            if ipmi_user in test_user:
                test_user.remove(ipmi_user)
            self.root.PUT('test_user',test_user)
            test_pass=opts.get('test_pass',['ADMIN','Admin','admin','root','Administrator'])
            if ipmi_pass in test_pass:
                test_pass.remove(ipmi_pass)
            self.root.PUT('test_pass',test_pass)
            self.root.PUT('ipmi_mode',opts.get('ipmi_mode',[Ipmitool()]))
            self.root.PUT('log_level',opts.get('log_level',5))
            self.root.PUT('timeout',opts.get('timeout',1800))
        if opts:
            if opts.get('ipmi_port',None):
                self.root.PUT('ipmi_port',opts.get('ipmi_port'))
            if opts.get('ipmi_ip',None):
                self.root.PUT('ipmi_ip',opts.get('ipmi_ip'))
                if not km.is_ipv4(self.root.GET('ipmi_ip')):
                    self.error(_type='ip',msg="{} is wrong IP Format".format(self.root.ipmi_ip.GET()))
                    km.logging(self.root.error.GET('ip'),log=self.log,log_level=1,dsp='e')
                elif not km.ping(self.root.GET('ipmi_ip'),count=0,timeout=600,log=self.log):
                    self.error(_type='ip',msg='Destination Host({}) Unreachable/Network problem'.format(self.root.ipmi_ip.GET()))
                    km.logging(self.root.error.GET('ip'),log=self.log,log_level=1,dsp='e')
                elif not km.is_port_ip(self.root.GET('ipmi_ip'),self.root.GET('ipmi_port')):
                    self.error(_type='ip',msg="{} is not IPMI IP".format(self.root.ipmi_ip.GET()))
                    km.logging(self.root.error.GET('ip'),log=self.log,log_level=1,dsp='e')
            if not self.root.error.GET('ip'):
                test_user=opts.get('test_user',None)
                test_pass=opts.get('test_pass',None)
                if opts.get('ipmi_user',None):
                    ipmi_user=opts.get('ipmi_user')
                    self.root.PUT('ipmi_user',ipmi_user)
#                    if not test_user:
#                        self.root.PUT('test_user',move2first(ipmi_user,self.root.test_user.GET()))
                if opts.get('uniq_pass',None):
                    upass=opts.get('uniq_pass')
                    self.root.PUT('uniq_pass',upass,proper={'readonly':True})
#                    if not test_pass:
#                        self.root.PUT('test_pass',move2first(upass,self.root.test_pass.GET()))
                if opts.get('ipmi_pass',None):
                    ipmi_pass=opts.get('ipmi_pass')
                    self.root.PUT('ipmi_pass',ipmi_pass)
#                    if not test_pass:
#                        self.root.PUT('test_pass',move2first(ipmi_pass,self.root.test_pass.GET()))
                if opts.get('ipmi_mac',None):
                    self.root.PUT('ipmi_mac',opts.get('ipmi_mac'),proper={'readonly':True})
                if not self.root.org_user.GET():
                    self.root.PUT('org_user',self.root.ipmi_user.GET(),proper={'readonly':True})
                if not self.root.org_pass.GET():
                    self.root.PUT('org_pass',self.root.ipmi_pass.GET(),proper={'readonly':True})
                if test_user:
                    self.root.PUT('test_user',move2first(self.root.ipmi_user.GET(),opts.get('test_user')))
                if test_pass:
                    self.root.PUT('test_pass',move2first(self.root.uniq_pass.GET(),opts.get('test_pass')))
                    self.root.PUT('test_pass',move2first(self.root.ipmi_pass.GET(),self.root.test_pass.GET()))
#                if opts.get('timeout',None):
#                    self.root.PUT('timeout',opts.get('timeout',1800))
#                if opts.get('ipmi_mode',None):
#                    self.root.PUT('ipmi_mode',opts.get('ipmi_mode'))
                if opts.get('rc',None):
                    self.root.PUT('rc',opts.get('rc',None))
                if opts.get('top_root',None):
                    self.top_root=kDict.kDict(opts.get('top_root'))
                    self.top_root.UPDATE(self.root.GET(),path='bmc')

    def redfish(self,**opts):
        cmd=opts.get('cmd','')
        sub_cmd=opts.get('sub_cmd',None)
        data=opts.get('data',None)
        files=opts.get('files',None)
        mode=opts.get('mode','get').lower()
        sub=opts.get('sub',False)
        rec=opts.get('rec',False)
        ipmi_ip=self.root.ipmi_ip.GET()
        ipmi_user=self.root.ipmi_user.GET()
        ipmi_pass=self.root.ipmi_pass.GET()
        def do_redfish(cmd,mode,sub_cmd=None,data=None,file=None):
           cmd_a=cmd.split(':')
           if cmd_a[0] == 'power' and cmd_a[1] in ['on','off','off_on','on_ff']:
               mode='post'
               cmd='Systems/1/Actions/ComputerSystem.Reset'
               if cmd_a[1] == 'on':
                   sub_cmd=[{'Action': 'Reset', 'ResetType': 'On'}]
               elif cmd_a[1] == 'off':
                   sub_cmd=[{'Action': 'Reset', 'ResetType': 'ForceOff'}]
               elif cmd_a[1] == 'off_on':
                   sub_cmd=[{'Action': 'Reset', 'ResetType': 'ForceOff'},{'Action': 'Reset', 'ResetType': 'On'}]
               elif cmd_a[1] == 'on_off':
                   sub_cmd=[{'Action': 'Reset', 'ResetType': 'On'},{'Action': 'Reset', 'ResetType': 'ForceOff'}]
           else:
               sub_cmd=[None]
               cmd_a=cmd.split('/')
               if len(cmd_a) > 2 and cmd_a[1] == 'redfish' and cmd_a[2] == 'v1':
                   cmd='/'.join(cmd_a[3:])
               if mode == 'put':
                   mode='post'
           for ss in sub_cmd:
               rc=km.web_req('https://{}/redfish/v1/{}'.format(ipmi_ip,cmd),user=ipmi_user,passwd=ipmi_pass,mode=mode,json=ss,data=data,files=files)
               if len(sub_cmd) > 1:
                   time.sleep(2)
           if rc[0] is False  or rc[1].status_code == 404:
               return False,'Error'
           else:
               return True,json.loads(rc[1].text)

        def get_cmd(dic):
           if type(dic) is dict and '@odata.id' in dic and len(dic) == 1:
               return True,dic['@odata.id']
           return False,dic

        def get_data(data=None,sub=False,rec=False):
           if data is None:
               data=do_redfish(cmd,'get')
           if sub:
               for key in data:
                   if type(data[key]) is list:
                       for ii in range(0,len(data[key])):
                           zz=get_cmd(data[key][ii])
                           if zz[0] is True:
                               zz_sub_data=do_redfish(zz[1],'get')
                               if rec:
                                   data[key][ii]=get_data(data=zz_sub_data,sub=True,rec=True)
                               else:
                                   data[key][ii]=zz_sub_data
                   else:
                       s_cmd=get_cmd(data[key])
                       if s_cmd[0] is True:
                           sub_data=do_redfish(s_cmd[1],'get')
                           if rec:
                               data[key]=get_data(data=sub_data,sub=True,rec=True)
                           else:
                               data[key]=sub_data
           return data

        if mode in ['put','post']:
            return do_redfish(cmd,'post')
        else:
            return get_data(sub=sub,rec=rec)

    def get_mode(self,name):
        for mm in self.root.ipmi_mode.GET():
            if mm.__name__ == name:
                return mm

    def info(self,**opts):
        rc={}
        rc['ipmi_ip']=self.root.ipmi_ip.GET()
        rc['ipmi_user']=self.root.ipmi_user.GET()
        rc['ipmi_pass']=self.root.ipmi_pass.GET()
        rc['ipmi_mode']=self.root.ipmi_mode.GET()
        rc['ipmi_mac']=self.root.ipmi_mac.GET()
        rc['ipmi_port']=self.root.ipmi_port.GET()
        if opts.pop('rf','dict') in ['tuple',tuple]:
            return True,rc['ipmi_ip'],rc['ipmi_user'],rc['ipmi_pass'],rc['ipmi_mode']
        else:
            return True,rc

    def init(self):
        ipmi_ip=self.root.GET('ipmi_ip')
        if not km.is_ipv4(ipmi_ip):
            return False,'IP Format Fail'
        if not km.is_port_ip(ipmi_ip,self.root.GET('ipmi_port')):
            return False,'It is not BMC IP'.format(ipmi_ip)
        rc=self.find_user_pass()
        if rc[0]:
            return True,'pass'
        return rc[0],rc[2]
        
    def is_tmp_pass(self,**opts):
        ipmi_ip=opts.get('ipmi_ip',self.root.ipmi_ip.GET())
        ipmi_user=opts.get('ipmi_user',self.root.ipmi_user.GET())
        ipmi_pass=opts.get('ipmi_pass',self.root.ipmi_pass.GET())
        tmp_pass=opts.get('tmp_pass',self.root.tmp_pass.GET())
        if tmp_pass and ipmi_pass != tmp_pass:
            new_str=opts.get('cmd_str','''ipmitool -I lanplus -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' chassis power status'''.format(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=tmp_pass))
            new_rc=km.rshell(new_str,timeout=2)
            if new_rc[0] == 0:
                old_str=opts.get('cmd_str','''ipmitool -I lanplus -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' chassis power status'''.format(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass))
                old_rc=km.rshell(old_str,timeout=2)
                if old_rc[0] != 0:
                    return True,tmp_pass,ipmi_pass
        return False,tmp_pass,ipmi_pass

    def find_user_pass(self,default_range=4,check_cmd='ipmi power status',cancel_func=None):
        ipmi_ip=self.root.ipmi_ip.GET()
        test_user=self.root.test_user.GET()
        test_pass=self.root.test_pass.GET()
        tmp_pass=self.root.tmp_pass.GET()
        log_level=self.root.log_level.GET()
        uniq_pass=self.root.GET('uniq_pass')
        ipmi_user=self.root.GET('ipmi_user')
        ipmi_pass=self.root.GET('ipmi_pass')
        test_user=move2first(ipmi_user,test_user)
        if len(test_pass) > default_range:
            tt=2
        else:
            tt=1
        for mm in self.root.ipmi_mode.GET():
            cmd_str=mm.cmd_str(check_cmd)
            for t in range(0,tt):
                if t == 0:
                    test_pass_sample=test_pass[:default_range]
                    if uniq_pass:
                        test_pass_sample=move2first(uniq_pass,test_pass_sample)
                    test_pass_sample=move2first(ipmi_pass,test_pass_sample)
                    if tmp_pass:
                        #test_pass_sample=[tmp_pass]+test_pass_sample
                        test_pass_sample=move2first(tmp_pass,test_pass_sample)
                else:
                    test_pass_sample=test_pass[default_range:]
                for uu in test_user:
                    for pp in test_pass_sample:
                        km.logging("""Try BMC User({}) and password({})""".format(uu,pp),log=self.log,log_level=7)
                        full_str=cmd_str[1].format(ipmi_ip=ipmi_ip,ipmi_user=uu,ipmi_pass=pp)
                        rc=km.rshell(full_str,timeout=2)
                        if rc[0] in cmd_str[3]['ok']:
                            km.logging("""Found working BMC User({}) and Password({})""".format(uu,pp),log=self.log,log_level=6)
                            self.root.PUT('ipmi_user',uu)
                            self.root.PUT('ipmi_pass',pp)
                            return True,uu,pp
                        else:
                            if km.is_lost(ipmi_ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=cancel_func)[0]:
                                return False,rc,'net error'
                        if log_level < 7:
                            km.logging("""x""".format(uu,pp),log=self.log,direct=True,log_level=3)
            km.logging("""Can not find working BMC User and password""",log=self.log,log_level=1,dsp='e')
            self.error(_type='user_pass',msg="Can not find working BMC User or password from POOL\nuser: {}\npassword:{}".format(self.root.GET('test_user'),self.root.GET('test_pass')))
        return False,None,None

    def recover_user_pass(self):
        mm=self.get_mode('smc')
        if not mm:
            return False,'SMCIPMITool module not found'
        ipmi_user=self.root.ipmi_user.GET()
        ipmi_pass=self.root.ipmi_pass.GET()
        org_user=self.root.org_user.GET()
        org_pass=self.root.org_pass.GET()
        tmp_pass=self.root.tmp_pass.GET()
        same_user=self.root.ipmi_user.CHECK(org_user)
        same_pass=self.root.ipmi_pass.CHECK(org_pass)
        if same_user and same_pass:
            km.logging("""Same user and passwrd. Do not need recover""",log=self.log,log_level=6)
            return True,self.root.ipmi_user.GET(),self.root.ipmi_pass.GET()
        if same_user:
            #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
            rc=self.run_cmd(mm.cmd_str("""user setpwd 2 '{}'""".format(org_pass)))
        else:
            #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
            rc=self.run_cmd(mm.cmd_str("""user add 2 {} '{}' 4""".format(org_user,org_pass)))
#        if rc[0]:
        if km.krc(rc[0],chk=True):
            km.logging("""Recovered BMC: from User({}) and Password({}) to User({}) and Password({})""".format(ipmi_user,ipmi_pass,org_user,org_pass),log=self.log,log_level=6)
            if tmp_pass:
                self.root.DEL('tmp_pass')
            self.root.PUT('ipmi_user',org_user)
            self.root.PUT('ipmi_pass',org_pass)
            return True,org_user,org_pass
        else:
            km.logging("""Not support {}. Looks need more length. So Try again with Super123""",log=self.log,log_level=6)
            if same_user:
                #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
                rrc=self.run_cmd(mm.cmd_str("""user setpwd 2 'Super123'"""))
            else:
                #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
                rrc=self.run_cmd(mm.cmd_str("""user add 2 {} 'Super123' 4""".format(org_user)))
            #if rrc[0]:
            if km.krc(rrc[0],chk=True):
                km.logging("""Recovered BMC: from User({}) and Password({}) to User({}) and Password(Super123)""".format(ipmi_user,ipmi_pass,org_user),log=self.log,log_level=6)
                if tmp_pass:
                    self.root.DEL('tmp_pass')
                self.root.PUT('ipmi_user',org_user)
                self.root.PUT('ipmi_pass','Super123')
                return True,org_user,'Super123'
            else:
                km.logging("""Recover ERROR!! Please checkup user-lock-mode on the BMC Configure.""",log=self.log,log_level=6)
                return False,ipmi_user,ipmi_pass
                
    def run_cmd(self,cmd,append=None,path=None,retry=0,timeout=None,return_code={'ok':[0,True],'fail':[]},show_str=False,dbg=False,mode='app',cancel_func=None,peeling=False,progress=False):
        error=self.error()
        #error=self.error(_type='break')
        if error[0]:
            return False,'''{}'''.format(error[1])
        # cmd format: <string> {ipmi_ip} <string2> {ipmi_user} <string3> {ipmi_pass} <string4>
        while peeling:
            if type(cmd)is tuple and len(cmd) == 1:
                cmd=cmd[0]
            else:
                break
        type_cmd=type(cmd)
        #if type_cmd in [tuple,list] and len(cmd) == 5 and type(cmd[0]) is bool:
        if type_cmd in [tuple,list] and len(cmd) >= 2 and type(cmd[0]) is bool:
            ok,cmd,path,return_code,timemout=tuple(km.get_value(cmd,[0,1,2,3,4]))
            if not ok:
                return False,(-1,'command format error(2)','command format error',0,0,cmd,path),'command({}) format error'.format(cmd)
        elif type_cmd is not str:
            return False,(-1,'command format error(3)','command format error',0,0,cmd,path),'command({}) format error'.format(cmd)
        rc_ok=return_code.get('ok',[0,True])
        rc_ignore=return_code.get('ignore',[])
        rc_fail=return_code.get('fail',[])
        rc_error=return_code.get('error',[127])
        rc_err_connection=return_code.get('err_connection',[])
        rc_err_key=return_code.get('err_key',[])
        rc_err_bmc_user=return_code.get('err_bmc_user',[])
        if type(append) is not str:
            append=''
        ipmi_ip=self.root.ipmi_ip.GET()
        ipmi_user=self.root.ipmi_user.GET()
        ipmi_pass=self.root.ipmi_pass.GET()
        for i in range(0,2+retry):
            if i > 1:
                km.logging('Re-try command [{}/{}]'.format(i,retry+1),log=self.log,log_level=1,dsp='d')
            if km.format_string_dict(cmd):
                cmd_str=km.format_string(cmd,{'ipmi_ip':ipmi_ip,'ipmi_user':ipmi_user,'ipmi_pass':ipmi_pass})[1] + append
            else:
                cmd_str=km.format_string(cmd,(ipmi_ip,ipmi_user,ipmi_pass))[1] + append

            if dbg or show_str:
                km.logging('** Do CMD  : {}'.format(cmd_str),log=self.log,log_level=1,dsp='d')
                km.logging(' - Timeout : %-15s - PATH    : %s'%(timeout,path),log=self.log,log_level=1,dsp='d')
                km.logging(' - CHK_CODE: {}\n'.format(return_code),log=self.log,log_level=1,dsp='d')
            try:
                if mode == 'redfish':
                    # code here for run redfish
                    # how to put sub, rec variable from kBmc?
                    start_time=km.int_sec()
                    rf_rt=self.redfish(cmd=cmd_str)
                    end_time=km.int_sec()
                    if type(rf_rt) is dict:
                        rf_rc=0
                    else:
                        rf_rc=1
                    rc=rf_rc,rf_rt,'',start_time,end_time,cmd_str,'web'
                else:
                    rc=km.rshell(cmd_str,path=path,timeout=timeout,progress=progress,log=self.log,progress_pre_new_line=True,progress_post_new_line=True)
            except:
                return 'error',(-1,'unknown','unknown',0,0,cmd,path),'Your command got error'
            if show_str:
                km.logging(' - RT_CODE : {}'.format(rc[0]),log=self.log,log_level=1,dsp='d')
            if dbg:
                km.logging(' - Output  : {}'.format(rc),log=self.log,log_level=1,dsp='d')
            if (not rc_ok and rc[0] == 0) or km.check_value(rc_ok,rc[0]):
                return True,rc,'ok'
            elif km.check_value(rc_err_connection,rc[0]): # retry condition1
                msg='err_connection'
                km.logging('Connection Error:',log=self.log,log_level=1,dsp='d',direct=True)
                #Check connection
                if km.is_lost(ipmi_ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=cancel_func)[0]:
                    km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                    return False,rc,'net error'
            elif km.check_value(rc_err_bmc_user,rc[0]): # retry condition1
                #Check connection
                if km.is_lost(ipmi_ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=cancel_func)[0]:
                    km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                    return False,rc,'net error'
                # Find Password
                ok,ipmi_user,ipmi_pass=self.find_user_pass()
                if not ok:
                    return False,'Can not find working IPMI USER and PASSWORD','user error'
                if dbg:
                    km.logging('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log=self.log,log_level=1,dsp='d')
                time.sleep(1)
            else:
                if 'ipmitool' in cmd_str and i < 1:
                    #Check connection
                    if km.is_lost(ipmi_ip,log=self.log,stop_func=self.error(_type='break')[0],cancel_func=cancel_func)[0]:
                        self.error(_type='ip',msg="{} lost network".format(ipmi_ip))
                        km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                        return False,rc,'net error'
                    # Find Password
                    ok,ipmi_user,ipmi_pass=self.find_user_pass()
                    if not ok:
                        return False,'Can not find working IPMI USER and PASSWORD','user error'
                    if dbg:
                        km.logging('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log=self.log,log_level=1,dsp='d')
                    time.sleep(1)
                else:
                    try:
                        if km.check_value(rc_ignore,rc[0]):
                            return 'ignore',rc,'return code({}) is in ignore condition({})'.format(rc[0],rc_ignore)
                        elif km.check_value(rc_fail,rc[0]):
                            return 'fail',rc,'return code({}) is in fail condition({})'.format(rc[0],rc_fail)
                        elif km.check_value([127],rc[0]):
                            return False,rc,'no command'
                        elif km.check_value(rc_error,rc[0]):
                            return 'error',rc,'return code({}) is in error condition({})'.format(rc[0],rc_error)
                        elif km.check_value(rc_err_key,rc[0]):
                            return 'error',rc,'return code({}) is in key error condition({})'.format(rc[0],rc_err_key)
                        elif isinstance(rc,tuple) and rc[0] > 0:
                            return 'fail',rc,'Not defined return-condition, So it will be fail'
                    except:
                        return 'unknown',rc,'Unknown result'
        return False,(-1,'timeout','timeout',0,0,cmd,path),'Time out the running command'

    def reset(self,ipmi={},retry=0,post_keep_up=20,pre_keep_up=0):
        ipmi_ip=self.root.ipmi_ip.GET()
        for i in range(0,1+retry):
            for mm in self.root.ipmi_mode.GET():
                if km.is_comeback(ipmi_ip,keep=pre_keep_up,log=self.log,stop_func=self.error(_type='break')[0]):
                    rc=self.run_cmd(mm.cmd_str('ipmi reset'))
                    if km.krc(rc[0],chk=True):
                        if km.is_comeback(ipmi_ip,keep=post_keep_up,log=self.log,stop_func=self.error(_type='break')[0]):
                            return True,'Pinging to BMC after reset BMC'
                        else:
                            return False,'Can not Pinging to BMC after reset BMC'
                else:
                    return False,'Can not Pinging to BMC. I am not reset the BMC. please check the network first!'
                time.sleep(5)
        return rc
            

    def get_mac(self):
        ipmi_mac=self.root.ipmi_mac.GET(default=None)
        if ipmi_mac:
            return True,ipmi_mac
        for mm in self.root.ipmi_mode.GET():
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan mac'))
            if km.krc(rc[0],chk=True):
#            if rc[0]:
                if name == 'smc':
                    self.root.PUT('ipmi_mac',[rc[1][1].lower()],proper={'readonly':True})
                    return True,[rc[1][1].lower()]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'MAC',0) and km.check_value(ii_a,'Address',1) and km.check_value(ii_a,':',2):
                            self.root.PUT('ipmi_mac',[ii_a[-1].lower()],proper={'readonly':True})
                            return True,[ii_a[-1].lower()]
        return False,[]

    def dhcp(self):
        for mm in self.root.ipmi_mode.GET():
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan dhcp'))
            if km.krc(rc[0],chk=True):
            #if rc[0]:
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'IP',0) and km.check_value(ii_a,'Address',1) and km.check_value(ii_a,'Source',2):
                            return True,ii_a[-2]
        return False,None

    def gateway(self):
        for mm in self.root.ipmi_mode.GET():
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan gateway'))
            if km.krc(rc[0],chk=True):
            #if rc[0]:
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'Default',0) and km.check_value(ii_a,'Gateway',1) and km.check_value(ii_a,'IP',2):
                            return True,ii_a[-1]
        return False,None

    def netmask(self):
        for mm in self.root.ipmi_mode.GET():
            name=mm.__name__
            rc=self.run_cmd(mm.cmd_str('ipmi lan netmask'))
            if km.krc(rc[0],chk=True):
            #if rc[0]:
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'Subnet',0) and km.check_value(ii_a,'Mask',1):
                            return True,ii_a[-1]
        return km.krc(rc[0]),None

    def bootorder(self,mode=None,ipxe=False,persistent=False,force=False,boot_mode={'smc':['pxe','bios','hdd','cd','usb'],'ipmitool':['pxe','ipxe','bios','hdd']}):
        available_module=self.root.ipmi_mode.GET()
        if not available_module:
            return False,'Not available module'
        rc=False,"Unknown boot mode({})".format(mode)
        for mm in available_module:
            name=mm.__name__
            chk_boot_mode=boot_mode[name]
            if name == 'smc' and mode in chk_boot_mode:
                if mode == 'pxe':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 1'))
                elif mode == 'hdd':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 2'))
                elif mode == 'cd':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 3'))
                elif mode == 'bios':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 4'))
                elif mode == 'usb':
                    rc=self.run_cmd(mm.cmd_str('ipmi power bootoption 6'))
                #if rc[0]:
                if km.krc(rc[0],chk=True):
                    return True,rc[1][1]
            elif name == 'ipmitool':
                #mm=self.get_mode('ipmitool')
                #if not mm:
                #    return False,'ipmitool module not found'
                if mode in [None,'order']:
                    rc=self.run_cmd(mm.cmd_str('chassis bootparam get 5'))
                    if mode == 'order':
                        if rc[0]:
                            rc=True,km.findstr(rc[1],'- Boot Device Selector : (\w.*)')[0]
                elif mode not in chk_boot_mode:
                    return False,'Unknown boot mode({}) at {}'.format(mode,name)
                else:
                    if persistent:
                        if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                            rc=self.run_cmd(mm.cmd_str('raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00'))
                        else:
                            rc=self.run_cmd(mm.cmd_str('chassis bootdev {0} options=persistent'.format(mode)))
                    else:
                        if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                            rc=self.run_cmd(mm.cmd_str('chassis bootdev {0} options=efiboot'.format(mode)))
                        else:
                            if force and chk_boot_mode == 'pxe':
                                rc=self.run_cmd(mm.cmd_str('chassis bootparam set bootflag force_pxe'.format(mode)))
                            else:
                                rc=self.run_cmd(mm.cmd_str('chassis bootdev {0}'.format(mode)))
                if km.krc(rc[0],chk=True):
                #if rc[0]:
                    return True,rc[1][1]
        return False,rc[-1]

    def get_eth_mac(self):
        eth_mac=self.root.eth_mac.GET(default=None)
        if eth_mac:
            return True,eth_mac
        for mm in self.root.ipmi_mode.GET():
            name=mm.__name__
            if name == 'ipmitool':
                aaa=mm.cmd_str('''raw 0x30 0x21''')
                rc=self.run_cmd(aaa)
                if km.krc(rc[0],chk=True):
                #if rc[0]:
                    mac=':'.join(rc[1][1].strip().split(' ')[-6:]).lower()
                    self.root.PUT('eth_mac',[mac])
                    return True,[mac]
            elif name == 'smc':
                rc=self.run_cmd(mm.cmd_str('ipmi oem summary | grep "System LAN"'))
                if km.krc(rc[0],chk=True):
                #if rc[0]:
                    rrc=[]
                    for ii in rc[1].split('\n'):
                        rrc.append(ii.split()[-1].lower())
                    self.root.PUT('eth_mac',rrc)
                    return True,rrc
        return False,[]

    def ping(self,test_num=3,retry=1,wait=1,keep=0,timeout=30): # BMC is on (pinging)
#        test_num=km.integer(test_num,default=3)
#        retry=km.integer(retry,default=1)
        retry=km.integer(retry,default=3)
        wait=km.integer(wait,default=1)
        keep=km.integer(keep,default=0)
        timeout=km.integer(timeout,default=30)
        #return km.ping(self.root.ipmi_ip.GET(),test_num=test_num,retry=retry,wait=wait,keep=keep,log=self.log)
        return km.ping(self.root.ipmi_ip.GET(),count=retry,interval=wait,keep_good=keep,log=self.log)

    def summary(self): # BMC is ready(hardware is ready)
        ipmi_ip=self.root.ipmi_ip.GET()
        ipmi_user=self.root.ipmi_user.GET()
        ipmi_pass=self.root.ipmi_pass.GET()
        if self.ping() is False:
            print('%10s : %s'%("Ping","Fail"))
            return False
        print('%10s : %s'%("Ping","OK"))
        print('%10s : %s'%("User",ipmi_user))
        print('%10s : %s'%("Password",ipmi_pass))
        ok,mac=self.get_mac()
        print('%10s : %s'%("Bmc Mac",'{}'.format(mac)))
        ok,eth_mac=self.get_eth_mac()
        if ok:
            print('%10s : %s'%("Eth Mac",'{}'.format(eth_mac)))
        print('%10s : %s'%("Power",'{}'.format(self.power('status'))))
        print('%10s : %s'%("DHCP",'{}'.format(self.dhcp()[1])))
        print('%10s : %s'%("Gateway",'{}'.format(self.gateway()[1])))
        print('%10s : %s'%("Netmask",'{}'.format(self.netmask()[1])))
        print('%10s : %s'%("LanMode",'{}'.format(self.lanmode()[1])))
        print('%10s : %s'%("BootOrder",'{}'.format(self.bootorder()[1])))

    #def node_state(self,state='up',timeout=600,keep_up=0,keep_down=0,interval=8, check_down=False,keep_unknown=180,**opts): # Node state
    def node_state(self,state='up',**opts): # Node state
        timeout=km.integer(opts.get('timeout'),default=600)
        keep_up=km.integer(opts.get('keep_up'),default=0)
        keep_down=km.integer(opts.get('keep_down'),default=0)
        power_down=km.integer(opts.get('power_down'),default=0)
        keep_unknown=km.integer(opts.get('keep_unknown'),default=180)
        interval=km.integer(opts.get('interval'),default=0)
        check_down=opts.get('check_down',False)
        if km.compare(keep_up,'>=',timeout,ignore=0):
            timeout=int(keep_up) + 30
        if km.compare(keep_down,'>=',timeout,ignore=0):
            timeout=int(keep_down) + 30
        stop_func=opts.get('stop_func',False)
        cancel_func=opts.get('cancel_func',False)
        # _: Down, -: Up, .: Unknown sensor data, !: ipmi sensor command error
        def sensor_data(cmd_str,name):
            krc=self.run_cmd(cmd_str)
            if km.krc(krc[0],chk=True):
                for ii in krc[1][1].split('\n'):
                    ii_a=ii.split('|')
                    find=''
                    if name == 'smc' and len(ii_a) > 2:
                        find=ii_a[1].strip()
                        tmp=ii_a[2].strip()
                    elif len(ii_a) > 4:
                        find=ii_a[0].strip()
                        tmp=ii_a[4].strip()
                    if 'Temp' in find and ('CPU' in find or 'System' in find):
                        if tmp == 'No Reading':
                            return 'unknown'
                        elif tmp in ['N/A','Disabled','0C/32F']:
                            return 'down'
                        else: # Up state
                            return 'up'
            return 'error'

        def power_data():
            pwr_info=self.power(cmd='status')
            return pwr_info.split()[-1]

        system_down=False
        init_time=0
        up_time=0
        down_time=0
        unknown_time=0
        no_read=0
        no_read_try=0
        power_down_time=0
        tmp=''
        while True:
            for mm in opts.get('ipmi_mode',self.root.ipmi_mode.GET()):
                name=mm.__name__
                cmd_str=mm.cmd_str('ipmi sensor')
                sensor_state=sensor_data(cmd_str,name)
                pwr_state=power_data()
                if stop_func is True:
                    km.logging('Got STOP Signal',log=self.log,log_level=1,dsp='e')
                    return False,'Got STOP Signal'            
                if cancel_func is True:
                    km.logging('Got Cancel Signal',log=self.log,log_level=1,dsp='e')
                    return False,'Got Cancel Signal'            
                if up_time > 0:
                    out,init_time=km.timeout(timeout+(keep_up*3),init_time)
                else:
                    out,init_time=km.timeout(timeout,init_time)
                if out:
                    km.logging('Node state Timeout',log=self.log,log_level=1,dsp='e')
                    if sensor_state == 'unknown':
                        self.root.UPDATE({'sensor':{km.int_sec():sensor_state}},path='error')
                    return False,'Node state Timeout over {} seconds'.format(timeout)
                if state == 'up':
                    if sensor_state == 'up':
                        down_time=0
                        up_ok,up_time=km.timeout(keep_up,up_time)
                        if up_ok:
                            if check_down:
                                if system_down:
                                    return True,'up'
                                else:
                                    return False,'up'
                            else:
                                return True,'up'
                    else:
                        up_time=0
                        if pwr_state == 'off':
                            dn_pw_ok,power_down_time=km.timeout(power_down,power_down_time)
                            if dn_pw_ok:
                                return False,'down'
                        else:
                            power_down_time=0
                        up_pw_ok,down_time=km.timeout(keep_down,down_time)
                        if up_pw_ok:
                            if pwr_state == 'on':
                                return False,'init'
                            else:
                                return False,'down'
                elif state == 'down':
                    system_down=True
                    if sensor_state == 'up':
                        down_time=0
                        dn_ok,up_time=km.timeout(keep_up,up_time)
                        if dn_ok:
                            return False,'up'
                    else:
                        up_time=0
                        if pwr_state == 'off':
                            dn_pw_ok,power_down_time=km.timeout(power_down,power_down_time)
                            if dn_pw_ok:
                                return True,'down'
                        else:
                            power_down_time=0
                        dn_pw_ok,down_time=km.timeout(keep_down,down_time)
                        if dn_pw_ok:
                            if pwr_state == 'on':
                                return False,'down' # Not real down
                            else:
                                return True,'down' # Real down

                if sensor_state == 'unknown': # No reading data
                    if keep_unknown > 0 and no_read_try < 2:
                        unknown_ok,unknown_time=km.timeout(keep_unknown,unknown_time)
                        if unknown_ok:
                             km.logging('[',log=self.log,direct=True,log_level=2)
                             rrst=self.reset()
                             km.logging(']',log=self.log,direct=True,log_level=2)
                             unknown_time=0
                             timeout=timeout+200
                             no_read_try+=1
                             if km.krc(rrst[0],chk=True):
                                 km.logging('O',log=self.log,direct=True,log_level=2)
                             else:
                                 km.logging('X',log=self.log,direct=True,log_level=2)
                    up_time=0
                    down_time=0
                    km.logging('.',log=self.log,direct=True,log_level=2)
                else:
                    unknown_time=0
                    if sensor_state == 'up':
                        km.logging('-',log=self.log,direct=True,log_level=2)
                    elif sensor_state == 'down':
                        km.logging('_',log=self.log,direct=True,log_level=2)
                    else: # error
                        up_time=0
                        down_time=0
                        km.logging('!',log=self.log,direct=True,log_level=2)
                time.sleep(interval)
            time.sleep(interval)

    def is_up(self,timeout=1200,keep_up=40,keep_down=300,power_down=20,interval=8,check_down=False,keep_unknown=180,**opts): # Node state
        return self.node_state(state='up',timeout=timeout,keep_up=keep_up,keep_down=keep_down,power_down=power_down,interval=interval,check_down=check_down,keep_unknown=keep_unknown,**opts) # Node state

    def is_down(self,timeout=1200,keep_up=240,interval=8,power_down=20,**opts): # Node state
        return self.node_state(state='down',timeout=timeout,keep_up=keep_up,interval=interval,power_down=power_down,**opts) # Node state

    def get_boot_mode(self):
        ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.info(rf='tuple')
        if ipmi_ok:
            return km.get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log=self.log)

    def power(self,cmd='status',retry=0,boot_mode=None,order=False,ipxe=False,log_file=None,log=None,force=False,mode=None,verify=True,post_keep_up=20,pre_keep_up=0,timeout=1200,lanmode=None):
        retry=km.integer(retry,default=0)
        timeout=km.integer(timeout,default=1200)
        pre_keep_up=km.integer(pre_keep_up,default=0)
        post_keep_up=km.integer(post_keep_up,default=20)
        if cmd == 'status':
            return self.do_power('status',verify=verify)[1]
        if boot_mode:
            km.logging('Set Boot mode to {} with iPXE({})\n'.format(boot_mode,ipxe),log=self.log,log_level=3)
            if ipxe in ['on','On',True,'True']:
                ipxe=True
            else:
                ipxe=False
            if boot_mode == 'ipxe':
                ipxe=True
                boot_mode='pxe'
            for ii in range(0,retry+1):
                # Find ipmi information
                ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.info(rf='tuple')
                km.set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,persistent=order,ipxe=ipxe,log_file=log_file,log=self.log,force=force)
                boot_mode_state=km.get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
                if (boot_mode == 'pxe' and boot_mode_state[0] is not False and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
                    break
                km.logging(' retry boot mode set {} (ipxe:{},force:{})[{}/5]'.format(boot_mode,ipxe,order,ii),log=self.log,log_level=6)
                time.sleep(2)
        return self.do_power(cmd,retry=retry,verify=verify,timeout=timeout,post_keep_up=post_keep_up,lanmode=lanmode)

    def do_power(self,cmd,retry=0,verify=False,timeout=1200,post_keep_up=40,pre_keep_up=0,lanmode=None):
        def lanmode_check(mode):
            # BMC Lan mode Checkup
            cur_lan_mode=self.lanmode()
            if cur_lan_mode[0]:
                if mode.lower() in cur_lan_mode[1].lower():
                    return mode
                else:
                    if mode == 'onboard':
                        rc=self.lanmode(mode=1)
                    elif mode == 'failover':
                        rc=self.lanmode(mode=2)
                    else:
                        rc=self.lanmode(mode=0)
                    if rc[0]:
                        return mode

        ipmi_ip=self.root.ipmi_ip.GET()
        timeout=self.root.timeout.GET()
        for mm in self.root.ipmi_mode.GET():
            name=mm.__name__
            if cmd not in ['status','off_on'] + list(mm.power_mode):
                return False,'Unknown command({})'.format(cmd)

            power_step=len(mm.power_mode[cmd])-1
            for ii in range(1,int(retry)+2):
                checked_lanmode=None
                init_rc=self.run_cmd(mm.cmd_str('ipmi power status'))
                if init_rc[0] is False:
                    km.logging('Power status got some error ({})'.format(init_rc[-1]),log=self.log,log_level=3)
                    time.sleep(3)
                    continue
                init_status=km.get_value(km.get_value(km.get_value(init_rc,1,[]),1,'').split(),-1)
                if verify is False or cmd == 'status':
                    if init_rc[0]:
                        if cmd == 'status':
                            return True,init_rc[1][1],ii
                        return True,rc[1][1],ii
                    time.sleep(3)
                    continue
                # keep command
                if pre_keep_up > 0 and self.is_up(timeout=timeout,keep_up=pre_keep_up)[0] is False:
                    time.sleep(3)
                    continue
                km.logging('Power {} at {} (try:{}/{}) (limit:{} sec)'.format(cmd,ipmi_ip,ii,retry+1,timeout),log=self.log,log_level=3)
                chk=1
                for rr in list(mm.power_mode[cmd]):
                    verify_status=rr.split(' ')[-1]
                    if chk == 1 and init_rc[0] and init_status == verify_status:
                        if chk == len(mm.power_mode[cmd]):
                            return True,verify_status,ii
                        chk+=1
                        continue
                    # BMC Lan mode Checkup before power on/cycle/reset
                    if checked_lanmode is None and lanmode and verify_status in ['on','reset','cycle']:
                       checked_lanmode=lanmode_check(lanmode)

                    if verify_status in ['reset','cycle']:
                         if init_status == 'off':
                             km.logging(' ! can not {} the power'.format(verify_status),log=self.log,log_level=6)
                             return [False,'can not {} the power'.format(verify_status)]
                    rc=self.run_cmd(mm.cmd_str(rr),retry=retry)
                    if km.krc(rc[0],chk=True):
                    #if rc[0] is True:
                        km.logging(' + Do power {}'.format(verify_status),log=self.log,log_level=6)
                        if verify_status in ['reset','cycle']:
                            verify_status='on'
                            time.sleep(10)
                    else:
                        km.logging(' ! power {} fail'.format(verify_status),log=self.log,log_level=6)
                        time.sleep(5)
                        break
                    if verify_status == 'on':
                        if self.is_up(timeout=timeout,keep_up=post_keep_up)[0]:
                            if chk == len(mm.power_mode[cmd]):
                                return True,'on',ii
                        time.sleep(3)
                    elif verify_status == 'off':
                        if self.is_down()[0]:
                            if chk == len(mm.power_mode[cmd]):
                                return True,'off',ii
                        time.sleep(3)
                    chk+=1
                time.sleep(3)
        return False,'time out',ii

    def lanmode(self,mode=None):
        mm=self.get_mode('smc')
        if not mm:
            km.logging(' - SMCIPMITool not found',log=self.log,log_level=1,dsp='e')
            return False,'SMCIPMITool not found'
        if mode in [0,1,2,'0','1','2']:
            rc=self.run_cmd(mm.cmd_str("""ipmi oem lani {}""".format(mode)))
        else:
            rc=self.run_cmd(mm.cmd_str("""ipmi oem lani"""))
        #if rc[0]:
        if km.krc(rc[0],chk=True):
            a=km.findstr(rc[1][1],'Current LAN interface is \[ (\w.*) \]')
            if len(a) == 1:
                return True,a[0]
        return False,None

    def error(self,_type=None,msg=None):
        if _type and msg:
#            self.root.UPDATE({'error':{_type:{km.int_sec():msg}}})
            self.root.UPDATE({_type:{km.int_sec():msg}},path='error')
        else:
            err=self.root.GET('error',default=None)
            if err is not None:
                if _type:
                    if err.get(_type,None) is not None:
                        return True,err[_type]
                err_user_pass=err.get('user_pass',None)
                if err_user_pass is not None:
                    if km.int_sec() - max(err_user_pass,key=int) < 10:
                        return True,'''ERR: BMC User/Password Error'''
                if err.get('break',None) is not None:
                    if km.int_sec() - max(err_user_pass,key=int) < 60:
                        return True,'''User want Stop Process'''
                return True,err
        return False,'OK'

    def rc_info(self,inp=None,default={},**opts):
        chk=True
        if inp:
            type_inp=type(inp)
            if type_inp is tuple and inp[0] is True and type(inp[1]) is dict:
                chk=False
                opts.update(inp[1])
            elif type_inp is dict:
                opts.update(inp)
        rf=opts.get('rf','dict')
        ok=opts.get('ok',default.get('ok',[0,True]))
        fail=opts.get('fail',default.get('fail',[]))
        error=opts.get('error',default.get('error',[127]))
        err_connection=opts.get('err_connection',default.get('err_connection',[]))
        err_key=opts.get('err_key',default.get('err_key',[]))
        err_bmc_user=opts.get('err_bmc_user',default.get('err_bmc_user',[]))
        if rf == 'tuple':
            return ok,fail,error,err_connection,err_bmc_user,err_key
        else:
            return {'ok':ok,'fail':fail,'error':error,'err_connection':err_connection,'err_bmc_user':err_bmc_user,'err_key':err_key}

if __name__ == "__main__":
    import sys
    import os
    def KLog(msg,**agc):
        direct=agc.get('direct',False)
        log_level=agc.get('log_level',6)
        ll=agc.get('log_level',5)
        if direct:
            sys.stdout.write(msg)
            sys.stdout.flush()
        elif log_level < ll:
            print(msg)

    tool_path='/django/sumViewer.5/tools'
    ipmi_ip='172.16.219.108'
    ipmi_user='ADMIN'
    ipmi_pass='ADMIN'
    ipxe=False
    print(sys.argv)
    if len(sys.argv) == 2 and sys.argv[1] in ['help','-h','--help']:
        print('{} -i <ipmi ip> -u <ipmi_user> -p <ipmi_pass> -t <tool path>'.format(sys.argv[0]))
        os._exit(1)

    for ii in range(1,len(sys.argv)):
        if sys.argv[ii] == '-i':
            ipmi_ip=sys.argv[ii+1]
        elif sys.argv[ii] == '-u':
            ipmi_user=sys.argv[ii+1]
        elif sys.argv[ii] == '-p':
            ipmi_pass=sys.argv[ii+1]
        elif sys.argv[ii] == '-t':
            tool_path=sys.argv[ii+1]
        elif sys.argv[ii] == '-ipxe':
            if sys.argv[ii+1] in ['true','True','on','On']:
                ipxe=True

    print('Test at {}'.format(ipmi_ip))
    bmc=kBmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool()])
    #bmc=BMC(root,ipmi_ip='172.16.220.135',ipmi_user='ADMIN',ipmi_pass='ADMIN',test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog)
#    print('Init')
#    bmc.init()
    print('Do')
#    print(bmc.is_up())
    print(bmc.bootorder()[1])
    print(bmc.power(cmd='status'))
#    print(bmc.power(cmd='off_on'))
#    print(bmc.power(cmd='reset'))
#    print(bmc.is_tmp_pass(ipmi_pass='Super123',tmp_pass='SumTester23'))
    #print(bmc.summary())
#    print(bmc.lanmode())
#    print(bmc.info())
#    print(bmc.get_mac())
    #print(bmc.run_cmd('Managers/1/Actions/Manager.Reset ',mode='redfish'))
    #print(bmc.run_cmd('Systems/1/Actions/ComputerSystem.Reset ',mode='redfish'))
#    print(bmc.run_cmd('Systems/1',mode='redfish'))
#    print(bmc.run_cmd('power:on',mode='redfish'))
#    print(bmc.run_cmd('power:off',mode='redfish'))
    #aa=bmc.reset()
    #print(aa)

