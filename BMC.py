# Kage Park
# Inteligent BMC Tool
# Version 2

import os
import time
import sys
import json
from klib.MODULE import MODULE
MODULE().Import('import klib.kmisc as km')
MODULE().Import('import klib.DICT as DICT')
MODULE().Import('import klib.LIST as LIST')
MODULE().Import('from klib.TIME import TIME')
MODULE().Import('from klib.SHELL import SHELL')
MODULE().Import('from klib.PING import ping')
MODULE().Import('from klib.IS import IS')

class Ipmitool:
    def __init__(self,**opts):
        self.__name__='ipmitool'
        self.tool_path=None
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status'],'shutdown':['chassis power soft']})
        self.ipmitool=True
        if not IS('ipmitool').Bin():
            self.ipmitool=False

    def Cmd_str(self,cmd,**opts):
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
        return True,{'base':'''ipmitool -I %s -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' '''%(option),'cmd':'''%s'''%(' '.join(cmd_a))},None,{'ok':[0],'fail':[1]},None


class Smcipmitool:
    def __init__(self,**opts):
        self.__name__='smc'
        self.tool_path=opts.get('tool_path',None)
        self.smc_file=None
        if self.tool_path and os.path.isdir(self.tool_path):
            self.smc_file='{}/{}'.format(self.tool_path,opts.get('smc_file',None))
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['ipmi power up'],'off':['ipmi power down'],'reset':['ipmi power reset'],'off_on':['ipmi power down','ipmi power up'],'on_off':['ipmi power up','ipmi power down'],'cycle':['ipmi power cycle'],'status':['ipmi power status'],'shutdown':['ipmi power softshutdown']})

    def Cmd_str(self,cmd,**opts):
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
        return True,{'base':'''sudo java -jar %s {ipmi_ip} {ipmi_user} '{ipmi_pass}' '''%(self.smc_file),'cmd':'''%s'''%(' '.join(cmd_a))},None,{'ok':[0,144],'error':[180],'err_bmc_user':[146],'err_connection':[145]},None

class Redfish:
    def __init__(self,**opts):
        self.__name__='redfish'
        self.log=opts.get('log',None)
        self.power_mode=opts.get('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status'],'shutdown':['chassis power soft']})

    def Cmd_str(self,cmd,**opts):
        return True,{'base':'''https://{ipmi_ip}/redfish/v1/%s'''%(cmd)},None,{'ok':[0,144],'error':[180],'err_bmc_user':[146],'err_connection':[145]},None

#def move2first(item,pool):
#    if item: 
#        if type(pool) is list and item in pool:
#            pool.remove(item)
#        return [item]+pool
#    return pool

class Bmc:
    def __init__(self,*inps,**opts):
        self.default_pass=opts.get('default_pass','Admin123')
        self.log=opts.get('log',None)
        if inps and type(inps[0]).__name__ == 'instance':
            self.root=inps[0].root
        else: 
            self.root=DICT()
            self.root.Put('ipmi_port',opts.get('ipmi_port',(623,664,443)))
            ipmi_user=opts.get('ipmi_user','ADMIN')
            self.root.Put('ipmi_user',ipmi_user)
            ipmi_pass=opts.get('ipmi_pass','ADMIN')
            self.root.Put('ipmi_pass',ipmi_pass)
            test_user=opts.get('test_user',['ADMIN','Admin','admin','root','Administrator'])
            if ipmi_user in test_user:
                test_user.remove(ipmi_user)
            self.root.Put('test_user',test_user)
            test_pass=opts.get('test_pass',['ADMIN','Admin','admin','root','Administrator'])
            if ipmi_pass in test_pass:
                test_pass.remove(ipmi_pass)
            self.root.Put('test_pass',test_pass)
            self.root.Put('ipmi_mode',opts.get('ipmi_mode',[Ipmitool()]))
            self.root.Put('log_level',opts.get('log_level',5))
            self.root.Put('timeout',opts.get('timeout',1800))
        if type(self.root.Get('timeout')) is not int:
            self.root.Put('timeout',600)
        if opts:
            if opts.get('ipmi_port',None):
                self.root.Put('ipmi_port',opts.get('ipmi_port'))
            if opts.get('ipmi_ip',None):
                self.root.Put('ipmi_ip',opts.get('ipmi_ip'))
                if not IS(self.root.Get('ipmi_ip')).Ipv4():
                    self.Error(_type='ip',msg="{} is wrong IP Format".format(self.root.ipmi_ip.Get()))
                    km.logging(self.root.error.Get('ip'),log=self.log,log_level=1,dsp='e')
                elif not ping(self.root.Get('ipmi_ip'),count=0,timeout=self.root.Get('timeout'),log=self.log):
                    self.Error(_type='ip',msg='Destination Host({}) Unreachable/Network problem'.format(self.root.ipmi_ip.Get()))
                    km.logging(self.root.error.Get('ip'),log=self.log,log_level=1,dsp='e')
                elif not km.is_port_ip(self.root.Get('ipmi_ip'),self.root.Get('ipmi_port')):
                    self.Error(_type='ip',msg="{} is not IPMI IP".format(self.root.ipmi_ip.Get()))
                    km.logging(self.root.error.Get('ip'),log=self.log,log_level=1,dsp='e')
            if not self.root.error.Get('ip'):
                test_user=opts.get('test_user',None)
                test_pass=opts.get('test_pass',None)
                if opts.get('ipmi_user',None):
                    ipmi_user=opts.get('ipmi_user')
                    self.root.Put('ipmi_user',ipmi_user)
                if opts.get('uniq_pass',None):
                    upass=opts.get('uniq_pass')
                    self.root.Put('uniq_pass',upass,proper={'readonly':True})
                if opts.get('ipmi_pass',None):
                    ipmi_pass=opts.get('ipmi_pass')
                    self.root.Put('ipmi_pass',ipmi_pass)
                if opts.get('ipmi_mac',None):
                    self.root.Put('ipmi_mac',opts.get('ipmi_mac'),proper={'readonly':True})
                if not self.root.org_user.Get():
                    self.root.Put('org_user',self.root.ipmi_user.Get(),proper={'readonly':True})
                if not self.root.org_pass.Get():
                    self.root.Put('org_pass',self.root.ipmi_pass.Get(),proper={'readonly':True})
                if test_user:
                    #self.root.Put('test_user',move2first(self.root.ipmi_user.Get(),opts.get('test_user')))
                    self.root.Put('test_user',LIST(opts.get('test_user')).Move2first(self.root.ipmi_user.Get()))
                if test_pass:
                    #self.root.Put('test_pass',move2first(self.root.uniq_pass.Get(),opts.get('test_pass')))
                    #self.root.Put('test_pass',move2first(self.root.ipmi_pass.Get(),self.root.test_pass.Get()))
                    self.root.Put('test_pass',LIST(opts.get('test_pass')).Move2first(self.root.uniq_pass.Get()))
                    self.root.Put('test_pass',LIST(self.root.test_pass.Get()).Move2first(self.root.ipmi_pass.Get()))
                if opts.get('rc',None):
                    self.root.Put('rc',opts.get('rc',None))
                if opts.get('top_root',None):
                    self.top_root=DICT(opts.get('top_root'))
                    self.top_root.Update(self.root.Get(),path='bmc')

    def Redfish(self,**opts):
        cmd=opts.get('cmd','')
        sub_cmd=opts.get('sub_cmd',None)
        data=opts.get('data',None)
        files=opts.get('files',None)
        mode=opts.get('mode','get').lower()
        sub=opts.get('sub',False)
        rec=opts.get('rec',False)
        ipmi_ip=self.root.ipmi_ip.Get()
        ipmi_user=self.root.ipmi_user.Get()
        ipmi_pass=self.root.ipmi_pass.Get()
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
                   TIME().Sleep(2)
           if rc[0] is False  or rc[1].status_code == 404:
               return False,'Error'
           else:
               return True,json.loads(rc[1].text)

        def Get_cmd(dic):
           if type(dic) is dict and '@odata.id' in dic and len(dic) == 1:
               return True,dic['@odata.id']
           return False,dic

        def Get_data(data=None,sub=False,rec=False):
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

    def Get_mode(self,name):
        for mm in self.root.ipmi_mode.Get():
            if mm.__name__ == name:
                return mm

    def Info(self,**opts):
        rc={}
        rc['ipmi_ip']=self.root.ipmi_ip.Get()
        rc['ipmi_user']=self.root.ipmi_user.Get()
        rc['ipmi_pass']=self.root.ipmi_pass.Get()
        rc['ipmi_upass']=self.root.uniq_pass.Get()
        rc['ipmi_mode']=self.root.ipmi_mode.Get()
        rc['ipmi_mac']=self.root.ipmi_mac.Get()
        rc['ipmi_port']=self.root.ipmi_port.Get()
        if opts.pop('rf','dict') in ['tuple',tuple]:
            return True,rc['ipmi_ip'],rc['ipmi_user'],rc['ipmi_pass'],rc['ipmi_mode']
        else:
            return True,rc

    def Init(self):
        ipmi_ip=self.root.Get('ipmi_ip')
        if not IS(ipmi_ip).Ipv4():
            self.Warn(_type='ip',msg="IP Format Fail")
            return False,'IP Format Fail'
        if not km.is_port_ip(ipmi_ip,self.root.Get('ipmi_port')):
            self.Warn(_type='ip',msg="It({}) is not BMC IP".format(ipmi_ip))
            return False,'It({}) is not BMC IP'.format(ipmi_ip)
        rc=self.Find_user_pass()
        if rc[0]:
            return True,'pass'
        return rc[0],rc[2]
        
    def Is_tmp_pass(self,**opts):
        ipmi_ip=opts.get('ipmi_ip',self.root.ipmi_ip.Get())
        ipmi_user=opts.get('ipmi_user',self.root.ipmi_user.Get())
        ipmi_pass=opts.get('ipmi_pass',self.root.ipmi_pass.Get())
        tmp_pass=opts.get('tmp_pass',self.root.tmp_pass.Get())
        if tmp_pass and ipmi_pass != tmp_pass:
            new_str=opts.get('cmd_str','''ipmitool -I lanplus -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' chassis power status'''.format(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=tmp_pass))
            new_rc=SHELL().Run(new_str,timeout=2)
            if new_rc[0] == 0:
                old_str=opts.get('cmd_str','''ipmitool -I lanplus -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' chassis power status'''.format(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass))
                old_rc=SHELL().Run(old_str,timeout=2)
                if old_rc[0] != 0:
                    return True,tmp_pass,ipmi_pass
        return False,tmp_pass,ipmi_pass

    def Find_user_pass(self,default_range=4,check_cmd='ipmi power status',cancel_func=None):
        ipmi_ip=self.root.ipmi_ip.Get()
        test_user=self.root.test_user.Get()
        test_pass=self.root.test_pass.Get()
        tmp_pass=self.root.tmp_pass.Get()
        log_level=self.root.log_level.Get()
        uniq_pass=self.root.Get('uniq_pass')
        ipmi_user=self.root.Get('ipmi_user')
        ipmi_pass=self.root.Get('ipmi_pass')
        test_user=LIST(test_user).Move2first(ipmi_user)
        #test_user=move2first(ipmi_user,test_user)
        tested_pass_sample=[]
        if len(test_pass) > default_range:
            tt=2
        else:
            tt=1
        for mm in self.root.ipmi_mode.Get():
            cmd_str=mm.Cmd_str(check_cmd)
            for t in range(0,tt):
                if t == 0:
                    test_pass_sample=test_pass[:default_range]
                else:
                    test_pass_sample=test_pass[default_range:]
                # Two times check for uniq,current,temporary password
                if uniq_pass:
                    #test_pass_sample=move2first(uniq_pass,test_pass_sample)
                    test_pass_sample=LIST(test_pass_sample).Move2first(uniq_pass)
                #test_pass_sample=move2first(ipmi_pass,test_pass_sample)
                test_pass_sample=LIST(test_pass_sample).Move2first(ipmi_pass)
                if tmp_pass:
                    #test_pass_sample=move2first(tmp_pass,test_pass_sample)
                    test_pass_sample=LIST(test_pass_sample).Move2first(tmp_pass)
                tested_pass_sample=tested_pass_sample+test_pass_sample
                for uu in test_user:
                    for pp in test_pass_sample:
                        km.logging("""Try BMC User({}) and password({})""".format(uu,pp),log=self.log,log_level=7)
                        full_str=cmd_str[1]['base'].format(ipmi_ip=ipmi_ip,ipmi_user=uu,ipmi_pass=pp)+' '+cmd_str[1]['cmd']
                        rc=SHELL().Run(full_str,timeout=2)
                        if rc[0] in cmd_str[3]['ok']:
                            km.logging("""Found working BMC User({}) and Password({})""".format(uu,pp),log=self.log,log_level=6)
                            self.root.Put('ipmi_user',uu)
                            self.root.Put('ipmi_pass',pp)
                            return True,uu,pp
                        else:
                            if km.is_lost(ipmi_ip,log=self.log,stop_func=self.Error(_type='break')[0],cancel_func=self.Cancel(cancel_func=cancel_func))[0]:
                                self.Warn(_type='net',msg="Network lost")
                                return False,rc,'net error'
                        if log_level < 7:
                            km.logging("""x""".format(uu,pp),log=self.log,direct=True,log_level=3)
            km.logging("""Can not find working BMC User and password""",log=self.log,log_level=1,dsp='e')
            self.Error(_type='user_pass',msg="Can not find working BMC User or password from POOL\nuser: {}\npassword:{}".format(test_user,tested_pass_sample))
        return False,None,None

    def Recover_user_pass(self,ipmi_user=None,ipmi_pass=None):
        mm=self.Get_mode('smc')
        if not mm:
            return False,'SMCIPMITool module not found'
        if ipmi_user is None:
            ipmi_user=self.root.ipmi_user.Get()
        if ipmi_pass is None:
            ipmi_pass=self.root.ipmi_pass.Get()
        org_user=self.root.org_user.Get()
        org_pass=self.root.org_pass.Get()
        tmp_pass=self.root.tmp_pass.Get()
        same_user=self.root.ipmi_user.CHECK(org_user)
        same_pass=self.root.ipmi_pass.CHECK(org_pass)
        if same_user and same_pass:
            km.logging("""Same user and passwrd. Do not need recover""",log=self.log,log_level=6)
            return True,self.root.ipmi_user.Get(),self.root.ipmi_pass.Get()
        if same_user:
            #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
            rc=self.Run_cmd(mm.Cmd_str("""user setpwd 2 '{}'""".format(org_pass)))
        else:
            #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
            rc=self.Run_cmd(mm.Cmd_str("""user add 2 {} '{}' 4""".format(org_user,org_pass)))
        if km.krc(rc[0],chk='error'):
            self.Warn(_type='ipmi_user',msg="Recover fail")
            return 'error',ipmi_user,ipmi_pass
        if km.krc(rc[0],chk=True):
            km.logging("""Recovered BMC: from User({}) and Password({}) to User({}) and Password({})""".format(ipmi_user,ipmi_pass,org_user,org_pass),log=self.log,log_level=6)
            if tmp_pass:
                self.root.DEL('tmp_pass')
            self.root.Put('ipmi_user',org_user)
            self.root.Put('ipmi_pass',org_pass)
            return True,org_user,org_pass
        else:
            km.logging("""Not support {}. Looks need more length. So Try again with {}""".format(self.default_pass),log=self.log,log_level=6)
            if same_user:
                #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
                rrc=self.Run_cmd(mm.Cmd_str("""user setpwd 2 '{}'""".format(self.default_pass)))
            else:
                #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
                rrc=self.Run_cmd(mm.Cmd_str("""user add 2 {} '{}' 4""".format(org_user,self.default_pass)))
            #if rrc[0]:
            if km.krc(rrc[0],chk=True):
                km.logging("""Recovered BMC: from User({}) and Password({}) to User({}) and Password({})""".format(ipmi_user,ipmi_pass,org_user,self.default_pass),log=self.log,log_level=6)
                if tmp_pass:
                    self.root.DEL('tmp_pass')
                self.root.Put('ipmi_user',org_user)
                self.root.Put('ipmi_pass','{}'.format(self.default_pass))
                return True,org_user,'{}'.format(self.default_pass)
            else:
                self.Warn(_type='ipmi_user',msg="Recover ERROR!! Please checkup user-lock-mode on the BMC Configure.")
                km.logging("""Recover ERROR!! Please checkup user-lock-mode on the BMC Configure.""",log=self.log,log_level=6)
                return False,ipmi_user,ipmi_pass
                
    def Run_cmd(self,cmd,append=None,path=None,retry=0,timeout=None,return_code={'ok':[0,True],'fail':[]},show_str=False,dbg=False,mode='app',cancel_func=None,peeling=False,progress=False):
        error=self.Error()
        #error=self.Error(_type='break')
        if error[0]:
            return 'error','''{}'''.format(error[1])
        # cmd format: <string> {ipmi_ip} <string2> {ipmi_user} <string3> {ipmi_pass} <string4>
        if not isinstance(return_code,dict):
            return_code={}
        while peeling:
            if type(cmd)is tuple and len(cmd) == 1:
                cmd=cmd[0]
            else:
                break
        type_cmd=type(cmd)
        if type_cmd in [tuple,list] and len(cmd) >= 2 and type(cmd[0]) is bool:
            ok,cmd,path,return_code,timemout=tuple(km.get_value(cmd,[0,1,2,3,4]))
            if not ok:
                self.Warn(_type='cmd',msg="command({}) format error".format(cmd))
                return False,(-1,'command format error(2)','command format error',0,0,cmd,path),'command({}) format error'.format(cmd)
        elif type_cmd is not str:
            self.Warn(_type='cmd',msg="command({}) format error".format(cmd))
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
        ipmi_ip=self.root.ipmi_ip.Get()
        ipmi_user=self.root.ipmi_user.Get()
        ipmi_pass=self.root.ipmi_pass.Get()
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
            if self.Cancel(cancel_func=cancel_func):
                km.logging(' !! Canceled Job',log=self.log,log_level=1,dsp='d')
                self.Warn(_type='cancel',msg="Canceled")
                return False,(-1,'canceled','canceled',0,0,cmd_str,path),'canceled'
            try:
                if mode == 'redfish':
                    # code here for run redfish
                    # how to put sub, rec variable from Bmc?
                    start_time=km.int_sec()
                    rf_rt=self.Redfish(cmd=cmd_str)
                    end_time=km.int_sec()
                    if type(rf_rt) is dict:
                        rf_rc=0
                    else:
                        rf_rc=1
                    rc=rf_rc,rf_rt,'',start_time,end_time,cmd_str,'web'
                else:
                    rc=SHELL().Run(cmd_str,path=path,timeout=timeout,progress=progress,log=self.log,progress_pre_new_line=True,progress_post_new_line=True)
            except:
                self.Warn(_type='cmd',msg="Your command got error({})")
                return 'error',(-1,'unknown','unknown',0,0,cmd_str,path),'Your command got error'
            if show_str:
                km.logging(' - RT_CODE : {}'.format(rc[0]),log=self.log,log_level=1,dsp='d')
            if dbg:
                km.logging(' - Output  : {}'.format(rc),log=self.log,log_level=1,dsp='d')
            if (not rc_ok and rc[0] == 0) or km.check_value(rc_ok,rc[0]):
                return True,rc,'ok'
            elif km.check_value(rc_err_connection,rc[0]): # retry condition1
                msg='err_connection'
                km.logging('Connection error condition:{}, return:{}'.format(rc_err_connection,rc[0]),log=self.log,log_level=7)
                km.logging('Connection Error:',log=self.log,log_level=1,dsp='d',direct=True)
                #Check connection
                if km.is_lost(ipmi_ip,log=self.log,stop_func=self.Error(_type='break')[0],cancel_func=self.Cancel(cancel_func=cancel_func))[0]:
                    km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                    #self.Warn(_type='net',msg="Lost network")
                    self.Error(_type='ip',msg="{} lost network(over 30min)".format(ipmi_ip))
                    return False,rc,'net error'
            elif km.check_value(rc_err_bmc_user,rc[0]): # retry condition1
                #Check connection
                if km.is_lost(ipmi_ip,log=self.log,stop_func=self.Error(_type='break')[0],cancel_func=self.Cancel(cancel_func=cancel_func))[0]:
                    self.Error(_type='ip',msg="{} lost network".format(ipmi_ip))
                    km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                    return False,rc,'net error'
                # Find Password
                ok,ipmi_user,ipmi_pass=self.Find_user_pass()
                if not ok:
                    self.Error(_type='ipmi_user',msg="Can not find working IPMI USER and PASSWORD")
#                    self.Warn(_type='ipmi_user',msg="Can not find working IPMI USER and PASSWORD")
                    return False,'Can not find working IPMI USER and PASSWORD','user error'
                if dbg:
                    km.logging('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log=self.log,log_level=1,dsp='d')
                TIME().Sleep(1)
            else:
                if 'ipmitool' in cmd_str and i < 1:
                    #Check connection
                    if km.is_lost(ipmi_ip,log=self.log,stop_func=self.Error(_type='break')[0],cancel_func=self.Cancel(cancel_func=cancel_func))[0]:
                        self.Error(_type='ip',msg="{} lost network".format(ipmi_ip))
                        km.logging('Lost Network',log=self.log,log_level=1,dsp='d')
                        return False,rc,'net error'
                    # Find Password
                    ok,ipmi_user,ipmi_pass=self.Find_user_pass()
                    if not ok:
                        self.Error(_type='ipmi_user',msg="Can not find working IPMI USER and PASSWORD")
                        return False,'Can not find working IPMI USER and PASSWORD','user error'
                    if dbg:
                        km.logging('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log=self.log,log_level=1,dsp='d')
                    TIME().Sleep(1)
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
        return False,(-1,'timeout','timeout',0,0,cmd_str,path),'Time out the running command'

    def Reset(self,ipmi={},retry=0,post_keep_up=20,pre_keep_up=0):
        ipmi_ip=self.root.ipmi_ip.Get()
        for i in range(0,1+retry):
            for mm in self.root.ipmi_mode.Get():
                if km.is_comeback(ipmi_ip,keep=pre_keep_up,log=self.log,stop_func=self.Error(_type='break')[0]):
                    km.logging('R',log=self.log,log_level=1,direct=True)
                    rc=self.Run_cmd(mm.Cmd_str('ipmi reset'))
                    if km.krc(rc[0],chk='error'):
                        return rc
                    if km.krc(rc[0],chk=True):
                        if km.is_comeback(ipmi_ip,keep=post_keep_up,log=self.log,stop_func=self.Error(_type='break')[0]):
                            return True,'Pinging to BMC after reset BMC'
                        else:
                            return False,'Can not Pinging to BMC after reset BMC'
                else:
                    return False,'Can not Pinging to BMC. I am not reset the BMC. please check the network first!'
                TIME().Sleep(5)
        return rc
            

    def Get_mac(self):
        ipmi_mac=self.root.ipmi_mac.Get(default=None)
        if ipmi_mac:
            return True,ipmi_mac
        for mm in self.root.ipmi_mode.Get():
            name=mm.__name__
            rc=self.Run_cmd(mm.Cmd_str('ipmi lan mac'))
            if km.krc(rc[0],chk='error'):
                return rc
            elif km.krc(rc[0],chk=True):
#            if rc[0]:
                if name == 'smc':
                    self.root.Put('ipmi_mac',[rc[1][1].lower()],proper={'readonly':True})
                    return True,[rc[1][1].lower()]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'MAC',0) and km.check_value(ii_a,'Address',1) and km.check_value(ii_a,':',2):
                            self.root.Put('ipmi_mac',[ii_a[-1].lower()],proper={'readonly':True})
                            return True,[ii_a[-1].lower()]
        return False,[]

    def Dhcp(self):
        for mm in self.root.ipmi_mode.Get():
            name=mm.__name__
            rc=self.Run_cmd(mm.Cmd_str('ipmi lan dhcp'))
            if km.krc(rc[0],chk='error'):
                return rc
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

    def Gateway(self):
        for mm in self.root.ipmi_mode.Get():
            name=mm.__name__
            rc=self.Run_cmd(mm.Cmd_str('ipmi lan gateway'))
            if km.krc(rc[0],chk='error'):
                return rc
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

    def Netmask(self):
        for mm in self.root.ipmi_mode.Get():
            name=mm.__name__
            rc=self.Run_cmd(mm.Cmd_str('ipmi lan netmask'))
            if km.krc(rc[0],chk='error'):
                return rc
            if km.krc(rc[0],chk=True):
                if name == 'smc':
                    return True,rc[1]
                elif name == 'ipmitool':
                    for ii in rc[1][1].split('\n'):
                        ii_a=ii.split()
                        if km.check_value(ii_a,'Subnet',0) and km.check_value(ii_a,'Mask',1):
                            return True,ii_a[-1]
        return km.krc(rc[0]),None

    def Bootorder(self,mode=None,ipxe=False,persistent=False,force=False,boot_mode={'smc':['pxe','bios','hdd','cd','usb'],'ipmitool':['pxe','ipxe','bios','hdd']}):
        available_module=self.root.ipmi_mode.Get()
        if not available_module:
            return False,'Not available module'
        rc=False,"Unknown boot mode({})".format(mode)
        for mm in available_module:
            name=mm.__name__
            chk_boot_mode=boot_mode[name]
            if name == 'smc' and mode in chk_boot_mode:
                if mode == 'pxe':
                    rc=self.Run_cmd(mm.Cmd_str('ipmi power bootoption 1'))
                elif mode == 'hdd':
                    rc=self.Run_cmd(mm.Cmd_str('ipmi power bootoption 2'))
                elif mode == 'cd':
                    rc=self.Run_cmd(mm.Cmd_str('ipmi power bootoption 3'))
                elif mode == 'bios':
                    rc=self.Run_cmd(mm.Cmd_str('ipmi power bootoption 4'))
                elif mode == 'usb':
                    rc=self.Run_cmd(mm.Cmd_str('ipmi power bootoption 6'))
                if km.krc(rc[0],chk=True):
                    return True,rc[1][1]
            elif name == 'ipmitool':
                #mm=self.Get_mode('ipmitool')
                #if not mm:
                #    return False,'ipmitool module not found'
                if mode in [None,'order']:
                    rc=self.Run_cmd(mm.Cmd_str('chassis bootparam get 5'))
                    if mode == 'order':
                        if rc[0]:
                            rc=True,km.findstr(rc[1],'- Boot Device Selector : (\w.*)')[0]
                elif mode not in chk_boot_mode:
                    self.Warn(_type='boot',msg="Unknown boot mode({}) at {}".format(mode,name))
                    return False,'Unknown boot mode({}) at {}'.format(mode,name)
                else:
                    if persistent:
                        if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                            rc=self.Run_cmd(mm.Cmd_str('raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00'))
                        else:
                            rc=self.Run_cmd(mm.Cmd_str('chassis bootdev {0} options=persistent'.format(mode)))
                    else:
                        if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                            rc=self.Run_cmd(mm.Cmd_str('chassis bootdev {0} options=efiboot'.format(mode)))
                        else:
                            if force and chk_boot_mode == 'pxe':
                                rc=self.Run_cmd(mm.Cmd_str('chassis bootparam set bootflag force_pxe'.format(mode)))
                            else:
                                rc=self.Run_cmd(mm.Cmd_str('chassis bootdev {0}'.format(mode)))
                if km.krc(rc[0],chk=True):
                    return True,rc[1][1]
            if km.krc(rc[0],chk='error'):
               return rc
        return False,rc[-1]

    def Get_eth_mac(self):
        eth_mac=self.root.eth_mac.Get(default=None)
        if eth_mac:
            return True,eth_mac
        rc=False,[]
        for mm in self.root.ipmi_mode.Get():
            name=mm.__name__
            if name == 'ipmitool':
                aaa=mm.Cmd_str('''raw 0x30 0x21''')
                rc=self.Run_cmd(aaa)
                if km.krc(rc[0],chk=True) and rc[1][1]:
                    mac_source=rc[1][1].split('\n')[0].strip()
                    if mac_source:
                        if len(mac_source.split()) == 10:  
                            mac=':'.join(mac_source.split()[-6:]).lower()
                        elif len(mac_source.split()) == 16:
                            mac=':'.join(mac_source.split()[-12:-6]).lower()
                        self.root.Put('eth_mac',[mac])
                        return True,[mac]
            elif name == 'smc':
                rc=self.Run_cmd(mm.Cmd_str('ipmi oem summary | grep "System LAN"'))
                if km.krc(rc[0],chk=True):
                    rrc=[]
                    for ii in rc[1].split('\n'):
                        rrc.append(ii.split()[-1].lower())
                    self.root.Put('eth_mac',rrc)
                    return True,rrc
            if km.krc(rc[0],chk='error'):
               return rc
        return False,[]

    def Ping(self,test_num=3,retry=1,wait=1,keep=0,timeout=30): # BMC is on (pinging)
        retry=km.integer(retry,default=3)
        wait=km.integer(wait,default=1)
        keep=km.integer(keep,default=0)
        timeout=km.integer(timeout,default=30)
        return ping(self.root.ipmi_ip.Get(),count=retry,interval=wait,keep_good=keep,log=self.log)

    def Summary(self): # BMC is ready(hardware is ready)
        ipmi_ip=self.root.ipmi_ip.Get()
        ipmi_user=self.root.ipmi_user.Get()
        ipmi_pass=self.root.ipmi_pass.Get()
        if self.ping() is False:
            print('%10s : %s'%("Ping","Fail"))
            return False
        print('%10s : %s'%("Ping","OK"))
        print('%10s : %s'%("User",ipmi_user))
        print('%10s : %s'%("Password",ipmi_pass))
        ok,mac=self.Get_mac()
        print('%10s : %s'%("Bmc Mac",'{}'.format(km.get_value(mac,0))))
        ok,eth_mac=self.Get_eth_mac()
        if ok:
            print('%10s : %s'%("Eth Mac",'{}'.format(km.get_value(eth_mac,0))))
        print('%10s : %s'%("Power",'{}'.format(self.Power('status'))))
        print('%10s : %s'%("DHCP",'{}'.format(self.Dhcp()[1])))
        print('%10s : %s'%("Gateway",'{}'.format(self.Gateway()[1])))
        print('%10s : %s'%("Netmask",'{}'.format(self.Netmask()[1])))
        print('%10s : %s'%("LanMode",'{}'.format(self.Lanmode()[1])))
        print('%10s : %s'%("BootOrder",'{}'.format(self.Bootorder()[1])))

    #def node_state(self,state='up',timeout=600,keep_up=0,keep_down=0,interval=8, check_down=False,keep_unknown=180,**opts): # Node state
    def Node_state(self,state='up',**opts): # Node state
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
        km.logging('Node state: timeout:{}, keep_up:{}, keep_down:{} power_down:{}, keep_unknown:{}, check_down:{}, stop:{}, cancel:{}'.format(timeout,keep_up,keep_down,power_down,keep_unknown,check_down,stop_func,cancel_func),log=self.log,log_level=7)
        # _: Down, -: Up, .: Unknown sensor data, !: ipmi sensor command error
        def sensor_data(cmd_str,name):
            krc=self.Run_cmd(cmd_str)
            if km.krc(krc[0],chk='error'):
               return 'error'
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
                            self.Warn(_type='sensor',msg="Can not read sensor data")
                            return 'unknown'
                        elif tmp in ['N/A','Disabled','0C/32F']:
                            return 'down'
                        else: # Up state
                            return 'up'
            return 'error'

        def power_data():
            pwr_info=self.Power(cmd='status')
            return pwr_info.split()[-1]

        bmc_modules=opts.get('ipmi_mode',self.root.ipmi_mode.Get())
        bmc_modules_num=len(bmc_modules)
        bmc_modules_chk=0
        system_down=False
        tmp=''
        for mm in bmc_modules:
            init_time=0
            up_time=0
            down_time=0
            no_read=0
            no_read_try=0
            power_down_time=0
            unknown_time=0
            bmc_modules_chk+=1
            name=mm.__name__
            cmd_str=mm.Cmd_str('ipmi sensor')
            while True:
                sensor_state=sensor_data(cmd_str,name)
                pwr_state=power_data()
                km.logging('Module:{}, Sensor state:{}, power_state:{}'.format(name,sensor_state,pwr_state),log=self.log,log_level=7)
                if stop_func is True:
                    km.logging('Got STOP Signal',log=self.log,log_level=1,dsp='e')
                    return False,'Got STOP Signal'            
                if self.Cancel(cancel_func=cancel_func):
                    km.logging('Got Cancel Signal',log=self.log,log_level=1,dsp='e')
                    return False,'Got Cancel Signal'            
                if up_time > 0:
                    out,init_time=km.timeout(timeout+(keep_up*3),init_time)
                else:
                    out,init_time=km.timeout(timeout,init_time)
                if out:
                    if bmc_modules_chk >= bmc_modules_num:
                        self.Warn(_type='timeout',msg="node_state()")
                        km.logging('Node state Timeout',log=self.log,log_level=1,dsp='e')
                        if sensor_state == 'unknown':
                            self.root.Update({'sensor':{km.int_sec():sensor_state}},path='error')
                        return False,'Node state Timeout over {} seconds'.format(timeout)
                    else:
                        # Change to Next checkup module
                        km.logging('{} state Timeout'.format(name),log=self.log,log_level=1,dsp='e')
                        break
                if state == 'up':
                    if sensor_state == 'up':
                        down_time=0
                        up_ok,up_time=km.timeout(keep_up,up_time)
                        if up_ok:
                            if check_down:
                                if system_down:
                                    km.logging('Good, Node is UP after down',log=self.log,log_level=7)
                                    return True,'up'
                                else:
                                    km.logging('Bad, Still UP',log=self.log,log_level=7)
                                    return False,'up'
                            else:
                                km.logging('Good, Node is UP',log=self.log,log_level=7)
                                return True,'up'
                    else:
                        up_time=0
                        if pwr_state == 'off':
                            system_down=True
                            dn_pw_ok,power_down_time=km.timeout(power_down,power_down_time)
                            if dn_pw_ok:
                                km.logging('Bad, Power is off (power_down over {}s)'.format(power_down),log=self.log,log_level=7)
                                return False,'down'
                        else:
                            power_down_time=0
                        up_pw_ok,down_time=km.timeout(keep_down,down_time)
                        if up_pw_ok:
                            if pwr_state == 'on':
                                km.logging('Bad, Power is on',log=self.log,log_level=7)
                                return False,'init'
                            else:
                                km.logging('Bad, Power is off (keep down over {}s)'.format(keep_down),log=self.log,log_level=7)
                                return False,'down'
                elif state == 'down':
                    if sensor_state == 'up':
                        down_time=0
                        dn_ok,up_time=km.timeout(keep_up,up_time)
                        if dn_ok:
                            km.logging('Bad, Node still up',log=self.log,log_level=7)
                            return False,'up'
                    else:
                        up_time=0
                        if pwr_state == 'off':
                            system_down=True
                            dn_pw_ok,power_down_time=km.timeout(power_down,power_down_time)
                            if dn_pw_ok:
                                km.logging('Good, Node is down',log=self.log,log_level=7)
                                return True,'down'
                        else:
                            power_down_time=0
                        dn_pw_ok,down_time=km.timeout(keep_down,down_time)
                        if dn_pw_ok:
                            if pwr_state == 'on':
                                km.logging('Bad, Power is up',log=self.log,log_level=7)
                                return False,'up' # Not real down
                            else:
                                km.logging('Good, Power is down',log=self.log,log_level=7)
                                return True,'down' # Real down

                if sensor_state == 'unknown': # No reading data
                    km.logging('Unknown state : keep check : {} < {}, no_read_try: {}, unknown_time:{} '.format(keep_unknown,km.int_sec()-unknown_time,no_read_try,unknown_time),log=self.log,log_level=7)
                    if keep_unknown > 0 and no_read_try < 2:
                        unknown_ok,unknown_time=km.timeout(keep_unknown,unknown_time)
                        km.logging('Unknown Timeout: {} < {} : {}'.format(keep_unknown,km.int_sec()-unknown_time,unknown_ok),log=self.log,log_level=7)
                        if unknown_ok:
                             km.logging('[',log=self.log,direct=True,log_level=2)
                             rrst=self.Reset()
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
                    km.logging('sensor_state: {}, unknown_time: {}'.format(sensor_state,unknown_time),log=self.log,log_level=7)
                    unknown_time=0
                    if sensor_state == 'up':
                        km.logging('-',log=self.log,direct=True,log_level=2)
                    elif sensor_state == 'down':
                        km.logging('_',log=self.log,direct=True,log_level=2)
                    else: # error
                        up_time=0
                        down_time=0
                        km.logging('!',log=self.log,direct=True,log_level=2)
                TIME().Sleep(interval)
            TIME().Sleep(interval)

    def Is_up(self,timeout=1200,keep_up=60,keep_down=240,power_down=30,interval=8,check_down=False,keep_unknown=300,**opts): # Node state
        timeout=km.integer(timeout,default=1200)
        keep_down=km.integer(keep_down,default=240)
        keep_up=km.integer(keep_up,default=60)
        power_down=km.integer(power_down,default=60)
        return self.Node_state(state='up',timeout=timeout,keep_up=keep_up,keep_down=keep_down,power_down=power_down,interval=interval,check_down=check_down,keep_unknown=keep_unknown,**opts) # Node state

    def Is_down(self,timeout=1200,keep_up=240,keep_down=30,interval=8,power_down=30,**opts): # Node state
        timeout=km.integer(timeout,default=1200)
        keep_up=km.integer(keep_up,default=240)
        keep_down=km.integer(keep_down,default=60)
        power_down=km.integer(power_down,default=60)
        return self.Node_state(state='down',timeout=timeout,keep_up=keep_up,interval=interval,power_down=power_down,**opts) # Node state

    def Get_boot_mode(self):
        ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.Info(rf='tuple')
        if ipmi_ok:
            return km.get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log=self.log)

    def Power(self,cmd='status',retry=0,boot_mode=None,order=False,ipxe=False,log_file=None,log=None,force=False,mode=None,verify=True,post_keep_up=20,pre_keep_up=0,timeout=1200,lanmode=None):
        retry=km.integer(retry,default=0)
        timeout=km.integer(timeout,default=1200)
        pre_keep_up=km.integer(pre_keep_up,default=0)
        post_keep_up=km.integer(post_keep_up,default=20)
        if cmd == 'status':
            return self.Do_power('status',verify=verify)[1]
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
                ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.Info(rf='tuple')
                km.set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,persistent=order,ipxe=ipxe,log_file=log_file,log=self.log,force=force)
                boot_mode_state=km.get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
                if (boot_mode == 'pxe' and boot_mode_state[0] is not False and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
                    break
                km.logging(' retry boot mode set {} (ipxe:{},force:{})[{}/5]'.format(boot_mode,ipxe,order,ii),log=self.log,log_level=6)
                TIME().Sleep(2)
        return self.Do_power(cmd,retry=retry,verify=verify,timeout=timeout,post_keep_up=post_keep_up,lanmode=lanmode)

    def Do_power(self,cmd,retry=0,verify=False,timeout=1200,post_keep_up=40,pre_keep_up=0,lanmode=None,cancel_func=None):
        timeout=km.integer(timeout,default=1200)
        def lanmode_check(mode):
            # BMC Lan mode Checkup
            cur_lan_mode=self.Lanmode()
            if cur_lan_mode[0]:
                if mode.lower() in cur_lan_mode[1].lower():
                    return mode
                else:
                    if mode == 'onboard':
                        rc=self.Lanmode(mode=1)
                    elif mode == 'failover':
                        rc=self.Lanmode(mode=2)
                    else:
                        rc=self.Lanmode(mode=0)
                    if rc[0]:
                        return mode

        ipmi_ip=self.root.ipmi_ip.Get()
        chkd=False
        for mm in self.root.ipmi_mode.Get():
            name=mm.__name__
            if cmd not in ['status','off_on'] + list(mm.power_mode):
                self.Warn(_type='power',msg="Unknown command({})".format(cmd))
                return False,'Unknown command({})'.format(cmd)

            power_step=len(mm.power_mode[cmd])-1
            for ii in range(1,int(retry)+2):
                checked_lanmode=None
                if verify or cmd == 'status':
                    init_rc=self.Run_cmd(mm.Cmd_str('ipmi power status'))
                    if km.krc(init_rc[0],chk='error'):
                        return init_rc[0],init_rc[1],ii
                    if init_rc[0] is False:
                        self.Warn(_type='power',msg="Power status got some error ({}))".format(init_rc[-1]))
                        km.logging('Power status got some error ({})'.format(init_rc[-1]),log=self.log,log_level=3)
                        TIME().Sleep(3)
                        continue
                    if cmd == 'status':
                        if init_rc[0]:
                            if cmd == 'status':
                                return True,init_rc[1][1],ii
                        TIME().Sleep(3)
                        continue
                    init_status=km.get_value(km.get_value(km.get_value(init_rc,1,[]),1,'').split(),-1)
                    if init_status == 'off' and cmd in ['reset','cycle']:
                        cmd='on'
                    # keep command
                    if pre_keep_up > 0 and self.Is_up(timeout=timeout,keep_up=pre_keep_up,cancel_func=cancel_func)[0] is False:
                        TIME().Sleep(3)
                        continue
                km.logging('Power {} at {} (try:{}/{}) (limit:{} sec)'.format(cmd,ipmi_ip,ii,retry+1,timeout),log=self.log,log_level=3)
                chk=1
                for rr in list(mm.power_mode[cmd]):
                    verify_status=rr.split(' ')[-1]
                    km.logging(' + Verify Status: "{}" from "{}"'.format(verify_status,rr),log=self.log,log_level=7)
                    if verify:
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
                                 self.Warn(_type='power',msg="Can not set {} on the off mode".format(verify_status))
                                 km.logging(' ! can not {} the power'.format(verify_status),log=self.log,log_level=6)
                                 return False,'can not {} the power'.format(verify_status)
                    rc=self.Run_cmd(mm.Cmd_str(rr),retry=retry)
                    km.logging('rr:{} cmd:{} rc:{}'.format(rr,mm.Cmd_str(rr),rc),log=self.log,log_level=8)
                    if km.krc(rc,chk='error'):
                        return rc
                    if km.krc(rc,chk=True):
                        km.logging(' + Do power {}'.format(verify_status),log=self.log,log_level=3)
                        if verify_status in ['reset','cycle']:
                            verify_status='on'
                            if verify:
                                TIME().Sleep(10)
                    else:
                        self.Warn(_type='power',msg="power {} fail".format(verify_status))
                        km.logging(' ! power {} fail'.format(verify_status),log=self.log,log_level=3)
                        TIME().Sleep(5)
                        break
                    if verify:
                        if verify_status in ['on','up']:
                            is_up=self.Is_up(timeout=timeout,keep_up=post_keep_up,cancel_func=cancel_func)
                            km.logging('is_up:{}'.format(is_up),log=self.log,log_level=7)
                            if is_up[0]:
                                if chk == len(mm.power_mode[cmd]):
                                    return True,'on',ii
                            elif is_up[1] == 'down' and not chkd:
                                chkd=True
                                self.Warn(_type='power',msg="Something weird. Looks BMC issue")
                                km.logging(' Something weird. Try again',log=self.log,log_level=1)
                                retry=retry+1 
                                TIME().Sleep(20)
                            TIME().Sleep(3)
                        elif verify_status in ['off','down']:
                            is_down=self.Is_down(cancel_func=cancel_func)
                            km.logging('is_down:{}'.format(is_down),log=self.log,log_level=7)
                            if is_down[0]:
                                if chk == len(mm.power_mode[cmd]):
                                    return True,'off',ii
                            elif is_down[1] == 'up' and not chkd:
                                chkd=True
                                self.Warn(_type='power',msg="Something weird. Looks BMC issue")
                                km.logging(' Something weird. Try again',log=self.log,log_level=1)
                                retry=retry+1 
                                TIME().Sleep(20)
                            TIME().Sleep(3)
                        chk+=1
                    else:
                        return True,km.get_value(km.get_value(rc,1),1),ii
                TIME().Sleep(3)
        if chkd:
            km.logging(' It looks BMC issue. (Need reset the physical power)',log=self.log,log_level=1)
            self.Error(_type='power',msg="It looks BMC issue. (Need reset the physical power)")
            return False,'It looks BMC issue. (Need reset the physical power)',ii
        return False,'time out',ii

    def Lanmode(self,mode=None):
        mm=self.Get_mode('smc')
        if not mm:
            km.logging(' - SMCIPMITool not found',log=self.log,log_level=1,dsp='e')
            return False,'SMCIPMITool not found'
        if mode in [0,1,2,'0','1','2']:
            rc=self.Run_cmd(mm.Cmd_str("""ipmi oem lani {}""".format(mode)))
        else:
            rc=self.Run_cmd(mm.Cmd_str("""ipmi oem lani"""))
        if km.krc(rc[0],chk='error'):
            return rc
        if km.krc(rc[0],chk=True):
            a=km.findstr(rc[1][1],'Current LAN interface is \[ (\w.*) \]')
            if len(a) == 1:
                return True,a[0]
        return False,None

    def Error(self,_type=None,msg=None):
        if _type and msg:
            self.root.Update({_type:{km.int_sec():msg}},path='error')
        else:
            err=self.root.Get('error',default={})
            if err:
                if _type:
                    if err.get(_type,None) is not None:
                        return True,err[_type]
                return True,err
        return False,'OK'

    def Warn(self,_type=None,msg=None):
        if _type and msg:
            self.root.Update({_type:{km.int_sec():msg}},path='warn')
        else:
            wrn=self.root.Get('warn',default={})
            if not wrn:
                if _type:
                    if wrn.get(_type,None) is not None:
                        return True,wrn[_type]
                return True,wrn
        return False,None

    def Cancel(self,cancel_func=None):
        if km.is_nancel(cancel_func):
            self.root.Update({km.int_sec():km.get_pfunction_name()},path='cancel')
            return 'canceled'
        else:
            revoke=self.root.Get('cancel',default={})
            if revoke:
                return revoke
        return False

    def Is_admin_user(self,**opts):
        admin_id=opts.get('admin_id',2)
        get_info=self.Info()
        if km.krc(get_info,chk=True):
            ipmi_info = km.get_value(get_info,1)
            for mm in self.root.ipmi_mode.Get():
                name=mm.__name__
                rc=self.Run_cmd(mm.Cmd_str("""user list"""))
                if km.krc(rc,chk=True):
                    for i in km.get_value(km.get_value(rc,1),1).split('\n'):
                        i_a=i.strip().split()
                        if str(admin_id) in i_a:
                            if km.get_value(i_a,-1) == 'ADMINISTRATOR':
                                if ipmi_info.get('ipmi_user') == km.get_value(i_a,1):
                                    return True
        return False
        

if __name__ == "__main__":
    import sys
    import os
    import pprint
    def KLog(msg,**agc):
        direct=agc.get('direct',False)
        log_level=agc.get('log_level',6)
        ll=agc.get('log_level',5)
        if direct:
            sys.stdout.write(msg)
            sys.stdout.flush()
        elif log_level < ll:
            print(msg)

    tool_path=km.get_my_directory()
    ipmi_user='ADMIN'
    ipmi_pass='ADMIN'
    ipxe=False
    smc_file=None
    ipmi_ip=None
    def help():
        print('{} -i <ipmi ip> [<OPT>] <cmd>'.format(sys.argv[0]))
        print('\n <OPT>')
        print(' -u <ipmi_user> : default ADMIN')
        print(' -p <ipmi_pass> : default ADMIN')
        print(' -t <tool path> : default PWD')
        print(' -si <SMCIPMITool file> ')
        print('\n <cmd>')
        print(' is_up          : node is UP?')
        print(' summary        : show summary')
        print(' bootorder      : show bootorder')
        print(' bootorder pxe  : Set PXE Boot mode')
        print(' bootorder ipxe : Set iPXE Boot mode')
        print(' bootorder bios : Set BIOS mode')
        print(' bootorder hdd  : Set HDD mode')
        print(' is_admin_user  : check current user is ADMINISTRATOR user?')
        print(' lanmode        : get current lanmode')
        print(' info           : show Info')
        print(' mac            : get BMC mac')
        print(' eth_mac        : get Ethernet Mac')
        print(' reset          : reset BMC')
        print(' power <status|reset|off|on|shutdown|cycle> : Send power signal')
        print(' vpower <status|reset|off|on|off_on|shutdown|cycle> : Send power signal and verify status')
#        print(' redfish <sub cmd>')
#        print('     power:on  : power on')
#        print('     power:off : power off')
#        print('     Systems/1 : Get Systems/1 information')
#        print('     Systems/1/Actions/ComputerSystem.Reset')
#        print('     Managers/1/Actions/Manager.Reset')
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
        elif sys.argv[ii] == '-si':
            smc_file=os.path.basename(sys.argv[ii+1])
            smc_path=os.path.dirname(sys.argv[ii+1])
        elif sys.argv[ii] == '-ipxe':
            if sys.argv[ii+1] in ['true','True','on','On']:
                ipxe=True
    if IS(ipmi_ip).Ipv4() is False or km.get_value(sys.argv,1) in ['help','-h','--help']:
        help()

    elif km.is_port_ip(ipmi_ip,(623,664,443)):
        print('Test at {}'.format(ipmi_ip))
        if smc_file and os.path.isfile('{}/{}'.format(tool_path,smc_file)):
            bmc=Bmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool(),Smcipmitool(tool_path=tool_path,smc_file=smc_file)])
        elif smc_file and os.path.isfile(smc_file):
            bmc=Bmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool(),Smcipmitool(tool_path=smc_path,smc_file=smc_file)])
        else:
            bmc=Bmc(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path,ipmi_mode=[Ipmitool()])

        cmd_2=km.get_value(sys.argv,-2)
        if cmd_2 == 'power':
            sub_cmd = km.get_value(sys.argv,-1)
            if sub_cmd == 'status':
                print(km.get_value(bmc.Do_power(cmd=sub_cmd),1))
            elif sub_cmd in ['on','off','reset','cycle','shutdown']:
                print(km.get_value(bmc.Do_power(cmd=sub_cmd),1))
            else:
                print('Unknown command "{}"'.format(sub_cmd))
        elif cmd_2 == 'vpower':
            sub_cmd = km.get_value(sys.argv,-1)
            if sub_cmd == 'status':
                print(bmc.power(cmd=sub_cmd))
            elif sub_cmd in ['on','off','off_on','reset','cycle','shutdown']:
                print(km.get_value(bmc.power(cmd=sub_cmd),1))
            else:
                print('Unknown command "{}"'.format(sub_cmd))
        elif cmd_2 == 'redfish':
            print(bmc.run_cmd(km.get_value(sys.argv,-1),mode='redfish'))
        elif cmd_2 == 'bootorder':
            mode=km.get_value(sys.argv,-1)
            if mode == 'ipxe':
                print(km.get_value(bmc.bootorder(mode='pxe',ipxe=True,persistent=True,force=True),1))
            else:
                print(km.get_value(bmc.bootorder(mode=mode,persistent=True,force=True),1))
        else:
            cmd=km.get_value(sys.argv,-1)
            if cmd == 'is_up':
                print(km.get_value(bmc.is_up(),1))
            elif cmd == 'bootorder':
                print(km.get_value(bmc.bootorder(),1))
            elif cmd == 'summary':
                print(bmc.summary())
            elif cmd == 'is_admin_user':
                print(bmc.Is_admin_user())
            elif cmd == 'lanmode':
                print(bmc.Lanmode())
            elif cmd == 'info':
                pprint.pprint(km.get_value(bmc.info(),1,default={}))
            elif cmd == 'mac':
                print(km.get_value(bmc.Get_mac(),1,default=['Can not get'])[0])
            elif cmd == 'eth_mac':
                print(km.get_value(bmc.get_eth_mac(),1,default=['Can not get'])[0])
            elif cmd == 'reset':
                print(km.get_value(bmc.reset(),1))
            else:
                print('Unknown command "{}"'.format(cmd))
                help()
    else:
        print('Looks the IP({}) is not BMC/IPMI IP or the BMC is not ready on network'.format(ipmi_ip))
