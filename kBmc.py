# Kage Park
# Inteligent BMC Tool

import os
from distutils.spawn import find_executable
import datetime
import time
import sys
import kmisc as km

class BMC:
    def __init__(self,root,ipmi_ip=None,ipmi_user=None,ipmi_pass=None,uniq_ipmi_pass=None,log=None,timeout=1800,tool_path=None,ipmi_mode='ipmitool',smc_file=None,test_user=[],test_pass=[],log_level=5):
        self.root=root
        self.log=log
        # Initial Dictionary
        if ipmi_ip and (km.is_ipv4(ipmi_ip) is False or km.is_ipmi_ip(ipmi_ip) is False):
            if self.log:
                self.log('{} is not IPMI IP\n'.format(ipmi_ip),log_level=1)
            else:
                sys.stderr.write('{} is not IPMI IP\n'.format(ipmi_ip))
                sys.stderr.flush()
            os._exit(1)
        else:
            self.root.bmc.PUT('ipmi_ip',ipmi_ip,new=True)
        self.test_user=['ADMIN','Admin','admin','root','Administrator']
        self.test_pass=['ADMIN','Admin','admin','root','Administrator']
        # If need update initial data then update
        self.root.bmc.PUT('timeout',timeout,{'readonly':True})
        self.root.bmc.PUT('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status']},{'readonly':True})
        self.root.bmc.PUT('ipmi_user',ipmi_user,{'readonly':True})
        self.root.bmc.PUT('ipmi_pass',ipmi_pass,{'readonly':True})
        self.root.bmc.PUT('cur_user',ipmi_user,new=True)
        self.root.bmc.PUT('cur_pass',ipmi_pass,new=True)
        for ii in test_user:
            if ii not in self.test_user:
                self.test_user.append(ii)
        for ii in test_pass:
            if ii not in self.test_pass:
                self.test_pass.append(ii)
        if self.root.bmc.ipmi_user.GET() in self.test_user:
            self.test_user.remove(self.root.bmc.ipmi_user.GET())
        self.root.bmc.PUT('test_user',[self.root.bmc.ipmi_user.GET()]+self.test_user,new=True)
        if uniq_ipmi_pass:
            self.root.bmc.PUT('uniq_pass',uniq_ipmi_pass,{'readonly':True})
            if uniq_ipmi_pass in self.test_pass:
                self.test_pass.remove(uniq_ipmi_pass)
            self.test_pass=[uniq_ipmi_pass]+self.test_pass
        if self.root.bmc.ipmi_pass.GET() in self.test_pass:
            self.test_pass.remove(self.root.bmc.ipmi_pass.GET())
        self.root.bmc.PUT('test_pass',[self.root.bmc.ipmi_pass.GET()]+self.test_pass,new=True)
        self.root.bmc.PUT('tool_path',tool_path,{'readonly':True})
        self.root.bmc.PUT('smc_file',smc_file,{'readonly':True})
        self.smc_file='/'.join(self.root.bmc.LIST(['tool_path','smc_file']))
        self.ipmitool=True
        if os.path.isfile(self.smc_file) is False:
            self.smc_file=None
            if ipmi_mode == 'smc':
                 if self.log:
                     self.log(' {} not found. So it changed mode to ipmi'.format(self.smc_file),log_level=1)
                     self.log(' go to https://www.supermicro.com/SwDownload/SwSelect_Free.aspx?cat=IPMI and download SMCIPMITool package',log_level=1)
        if find_executable('ipmitool') is False:
             self.ipmitool=False
             if self.log:
                 self.log(' ipmitool package not found',log_level=1)
                 self.log(' Install ipmitool package(yum install ipmitool)',log_level=1)
        if self.root.bmc.ipmi_mode.PROPER('readonly'):
            self.root.bmc.ipmi_mode.PROPER('readonly',False)
        if self.smc_file and self.ipmitool:
            if ipmi_mode == 'smc':
                self.root.bmc.PUT('ipmi_mode',['smc','ipmitool'],{'readonly':True})
            else:
                self.root.bmc.PUT('ipmi_mode',['ipmitool','smc'],{'readonly':True})
        elif self.ipmitool:
            self.root.bmc.PUT('ipmi_mode',['ipmitool'],{'readonly':True})
        elif self.smc_file:
            self.root.bmc.PUT('ipmi_mode',['smc'],{'readonly':True})
        else:
            km.logging("SMCIPMITool and ipmitool not found",log=self.log,log_level=6,dsp='e')
            os._exit(1)

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

    def ipmi_info(self,inp=None,**opts):
        chk=True
        if inp:
            type_inp=type(inp)
            if type_inp is tuple and inp[0] is True and type(inp[1]) is dict:
                chk=False
                opts.update(inp[1])
            elif type_inp is dict:
                opts.update(inp)
        rf=opts.get('rf','dict')
        default=opts.get('default',None)
        ipmi_ip=opts.get('ipmi_ip',default)
        if ipmi_ip is default:
            ipmi_ip=self.root.bmc.ipmi_ip.GET(default=default)
            if ipmi_ip is default:
                return False,{'err':'{} is not IPMI IP'.format(ipmi_ip)}
        elif chk:
            if km.is_ipv4(ipmi_ip) is False or km.is_ipmi_ip(ipmi_ip) is False:
                return False,{'err':'{} is not IPMI IP'.format(ipmi_ip)}
        cur_user=opts.get('cur_user',default)
        if cur_user:
            self.root.bmc.PUT('cur_user',cur_user)
            ipmi_user=cur_user
        else:
            ipmi_user=opts.get('ipmi_user',self.root.bmc.cur_user.GET())
        cur_pass=opts.get('cur_pass',default)
        if cur_pass:
            self.root.bmc.PUT('cur_pass',cur_pass)
            ipmi_pass=cur_pass
        else:
            ipmi_pass=opts.get('ipmi_pass',self.root.bmc.cur_pass.GET())
        ipmi_mode=opts.get('ipmi_mode',self.root.bmc.ipmi_mode.GET())
        if rf == 'tuple':
            return True,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode
        else:
            return True,{'ipmi_ip':ipmi_ip,'ipmi_user':ipmi_user,'ipmi_pass':ipmi_pass,'ipmi_mode':ipmi_mode}

    def bmc_cmd(self,cmd,**opts):
        error=self.root.bmc.GET('error',default=None)
        if error:
            return False,'''BMC Error: {}'''.format(error)
        ipmi=self.ipmi_info(opts.get('ipmi',None),**opts)
        option=opts.get('option','lanplus')
        cmd_a=cmd.split()
        ipmi_mode=ipmi[1]['ipmi_mode']
        if isinstance(ipmi_mode,list):
            ipmi_mode=ipmi_mode[0]
        if ipmi_mode == 'smc':
            if self.smc_file is None:
                if self.log:
                    self.log(' - SMCIPMITool({}) not found'.format(self.smc_file),log_level=5)
                return False,'SMCIPMITool file not found'
            if km.value_check(cmd_a,'chassis',0) and km.value_check(cmd_a,'power',1):
                cmd_a[0] == 'ipmi'
            elif km.value_check(cmd_a,'mc',0) and km.value_check(cmd_a,'reset',1) and km.value_check(cmd_a,'cold',2):
                cmd_a=['ipmi','reset']
            elif km.value_check(cmd_a,'lan',0) and km.value_check(cmd_a,'print',1):
                cmd_a=['ipmi','lan','mac']
            elif km.value_check(cmd_a,'sdr',0) and km.value_check(cmd_a,'Temperature',2):
                cmd_a=['ipmi','sensor']
            return True,'''sudo java -jar %s {ipmi_ip} {ipmi_user} '{ipmi_pass}' %s'''%(self.smc_file,' '.join(cmd_a))
        elif ipmi_mode in ['ipmitool',None]:
            if self.ipmitool is False:
                if self.log:
                    self.log('ipmitool package not found',log_level=5)
                return False,'ipmitool package not found'
            if km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'power',1) and km.get_value(cmd_a,2) in self.root.bmc.power_mode.GET():
                cmd_a[0] = 'chassis'
            elif km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'reset',1):
                cmd_a=['mc','reset','cold']
            elif km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'lan',1) and km.value_check(cmd_a,'mac',2):
                cmd_a=['lan','print']
            elif km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'sensor',1):
                cmd_a=['sdr','type','Temperature']
            return True,'''ipmitool -I %s -H {ipmi_ip} -U {ipmi_user} -P '{ipmi_pass}' %s'''%(option,' '.join(cmd_a))
        return False,'''Unknown mode({})'''.format(ipmi_mode)

    def check_passwd(self,**opts):
        ipmi=self.ipmi_info(**opts)
        if ipmi[0]:
            bmc_cmd=self.bmc_cmd('ipmi power status',ipmi_mode=ipmi[1]['ipmi_mode'])
            if bmc_cmd[0]:
                if self.run_cmd(bmc_cmd[1],ipmi=ipmi,return_code=self.rc_info(ok=[0],fail=[1]))[0]: # if remove return_code's fail=[1] then it will be infinity call looping between check_passwd() and run_cmd()
                    return True
        return False

    def find_user_pass(self,ipmi_user=None,ipmi_pass=None):
        test_user_a=self.root.bmc.test_user.GET()[:]
        test_pass_a=self.root.bmc.test_pass.GET()[:]
        default_range=3
        ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.ipmi_info(ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,rf='tuple')
        if ipmi_ok is False:
            return False,None,None
        # ipmi user
        if ipmi_user:
            if ipmi_user in test_user_a:
                test_user_a.remove(ipmi_user)
            test_user_a=['{}'.format(ipmi_user)] + test_user_a
        # ipmi password
        if ipmi_pass:
            if ipmi_pass in test_pass_a:
                test_pass_a.remove(ipmi_pass)
                default_range -= 1
            test_pass_a=['''{}'''.format(ipmi_pass)] + test_pass_a
            default_range += 1
        # Find in default's information
        for uu in test_user_a:
            for pp in test_pass_a[:default_range]:
                if self.log:
                    self.log(' !! Try BMC password({}) and User({})'.format(pp,uu),log_level=6)
                if self.check_passwd(ipmi_user=uu,ipmi_pass=pp):
                    self.root.bmc.PUT('cur_user',uu)
                    self.root.bmc.PUT('cur_pass',pp)
                    if self.log:
                        self.log(' !! Found working BMC password({}) and User({})'.format(pp,uu),log_level=7)
                    return True,uu,pp
        # Find in others temporary random passwords
        if len(test_pass_a) > default_range:
            for uu in test_user_a:
                for pp in test_pass_a[default_range:]:
                    if self.log:
                        self.log(' !! Try BMC password({}) and User({})'.format(pp,uu),log_level=8)
                    if self.check_passwd(ipmi_user=uu,ipmi_pass=pp):
                        if self.log:
                            self.log(' !! Found working BMC password({}) and User({})'.format(pp,uu),log_level=7)
                        self.root.bmc.PUT('cur_user',uu)
                        self.root.bmc.PUT('cur_pass',pp)
                        return True,uu,pp
        if self.log:
            self.log(' Can not find working BMC User and password',log_level=1)
            self.root.bmc.UPDATE({'error':{'user_pass':{int(datetime.datetime.now().strftime('%s')):'Can not find working BMC User or password'}}})
        return False,None,None
###########################

    def recover_user_pass(self,cur_user=None,cur_pass=None):
        if self.smc_file is None:
            if self.log:
                self.log(' - SMCIPMITool({}) not found'.format(self.smc_file),log_level=5)
            return False,cur_user,cur_pass
        ok,ipmi_user,ipmi_pass=self.find_user_pass(ipmi_user=cur_user,ipmi_pass=cur_pass)
        if ok is False:
            if self.log:
                self.log(' - Can not find working User and Password (Input:({},{}), ({},{}))'.format(cur_user,cur_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),log_level=1)
                return False,cur_user,cur_pass
        if cur_user and cur_pass and ( cur_user != ipmi_user or cur_pass != ipmi_pass ):
            if self.log:
                self.log(' - Found New BMC Info (User({}) and Password({})) from User({}) and Password({})'.format(ipmi_user,ipmi_pass,cur_user,cur_pass),log_level=1)

        if self.root.bmc.ipmi_user.CHECK(ipmi_user) and self.root.bmc.ipmi_pass.CHECK(ipmi_pass):
            if self.log:
                self.log(' - Same user and passwrd. Do not need recover',log_level=6)
            return True,ipmi_user,ipmi_pass
        if self.root.bmc.ipmi_user.CHECK(ipmi_user): # same user but changed password
            #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
            bmc_cmd=self.bmc_cmd("""user setpwd 2 '{}'""".format(self.root.bmc.ipmi_pass.GET()),ipmi_mode='smc')
        else: # changed user and password
            #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
            bmc_cmd=self.bmc_cmd("""user add 2 {} '{}' 4""".format(self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),ipmi_mode='smc')
        if bmc_cmd[0] is False:
            return bmc_cmd
        rc=self.do_cmd(bmc_cmd[1])
        if rc[0] == 0:
            if self.log:
                self.log(' - Recovered BMC: from User({}) and Password({}) to User({}) and Password({})'.format(ipmi_user,ipmi_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),log_level=6)
            return True,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()
        else:
            if self.log:
                log(' - Not support {}. Looks need more length. So Try again with Super123'.format(ipmi_pass),log_level=6)
            if self.root.bmc.ipmi_user.CHECK(ipmi_user): # SAME user 
                bmc_cmd=self.bmc_cmd("""user setpwd 2 Super123""",ipmi_mode='smc')
            else: # different user and password
                bmc_cmd=self.bmc_cmd("""user add 2 {} Super123 4""".format(self.root.bmc.ipmi_user.GET()),ipmi_mode='smc')
            rc=km.do_cmd(bmc_cmd[1])
            if rc[0] == 0:
                if self.log:
                    self.log(' - Recovered BMC with Super123: from User({}) and Password({}) to User({}) and Password(Super123)'.format(ipmi_user,ipmi_pass,self.root.bmc.ipmi_user.GET()),log_level=6)
                return True,self.root.bmc.ipmi_user.GET(),'Super123'
            else:
                if self.log:
                    self.log(' - Recover BMC ERROR !!! : from User({}) and Password ({}) to User({}) and Password({})\n{}'.format(ipmi_user,ipmi_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET(),rc),log_level=6)
                return False,ipmi_user,ipmi_pass

    def run_cmd(self,cmd,append=None,path=None,retry=0,timeout=None,ipmi={},return_code={'ok':[0,True],'fail':[]}):
        # cmd format: <string> {ipmi_ip} <string2> {ipmi_user} <string3> {ipmi_pass} <string4>
        if type(cmd) is tuple and len(cmd) == 3:
            cmd,path,return_code=cmd
        rc_ok=return_code.get('ok',[0,True])
        rc_fail=return_code.get('fail',[])
        rc_error=return_code.get('error',[127])
        rc_err_connection=return_code.get('err_connection',[])
        rc_err_key=return_code.get('err_key',[])
        rc_err_bmc_user=return_code.get('err_bmc_user',[])
        if type(append) is not str:
            append=''
        error=self.root.bmc.GET('error',default=None)
        if error:
            return False,'''BMC Error: {}'''.format(error)
        ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.ipmi_info(ipmi,rf='tuple')
        if ipmi_ok:
            for i in range(0,2+retry):
                if self.log and i > 1:
                    self.log('Re-try command [{}/{}]'.format(i,retry+1),log_level=1)
                cmd_str=cmd.format(ipmi_ip=ipmi_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass)+append
                rc=km.rshell(cmd_str,path=path,timeout=timeout)
                if km.check_value(rc[0],rc_ok):
                    return True,rc,'ok'
                elif km.check_value(rc[0],rc_fail):
                    return False,rc,'fail'
                elif km.check_value(rc[0],[127]):
                    return False,rc,'no command'
                elif km.check_value(rc[0],rc_error):
                    return False,rc,'error'
                elif km.check_value(rc[0],rc_err_key):
                    return False,rc,'err_key'
                elif km.check_value(rc[0],rc_err_connection):
                    # retry again 
                    msg='err_connection'
                    if self.log:
                        self.log('Connection Error:',direct=True,log_level=1)
                    init_time=None
                    while True:
                        if self.log:
                            self.log('.',direct=True,log_level=1)
                        ttt,init_time=km.timeout(timeout,init_time)
                        if ttt:
                            return False,rc,'net error'
                        if self.ping(ipmi_ip):
                            if self.log:
                                self.log(' ',log_level=1)
                            break
                        time.sleep(5)
                else:
                    if km.check_value(rc[0],rc_err_bmc_user):
                        ok,ipmi_user,ipmi_pass=self.find_user_pass(ipmi_user=ipmi_user,ipmi_pass=ipmi_pass)
                        if ok is False:
                            return False,'Can not find working IPMI USER and PASSWORD','user error'
                        if self.log:
                            self.log('Check IPMI User and Password: Found ({}/{})'.format(ipmi_user,ipmi_pass),log_level=5)
                    time.sleep(1)
        return False,(-1,'timeout','timeout',0,0,cmd,path),'user error'

    def do_cmd(self,cmd,path=None,retry=0,timeout=None,ipmi={},return_code={'ok':[0,True],'fail':[]}):
        if type(cmd) is tuple and len(cmd) == 3:
            cmd,path,return_code=cmd
        def get_bmc_cmd(ipmi_mode):
            bmc_cmd=[]
            if ipmi_mode in ['all','*']:
                for ii in self.bmc.ipmi_mode.GET():
                    chk_cmd=self.bmc_cmd(cmd,ipmi_mode=ii)
                    if chk_cmd[0]:
                        bmc_cmd.append(chk_cmd[1])
            else:
                chk_cmd=self.bmc_cmd(cmd,ipmi_mode=ipmi_mode)
                if chk_cmd[0]:
                    bmc_cmd.append(chk_cmd[1])
            return bmc_cmd

        ipmi=self.ipmi_info(ipmi)
        if ipmi[0] is False:
            return False,'Wrong IP'
        ipmi_mode=ipmi[1].get('ipmi_mode',None)
        bmc_cmd=get_bmc_cmd(ipmi_mode)
        if len(bmc_cmd) == 0:
            if self.log:
                self.log(' - SMCIPMITool and ipmitool package not found',log_level=5)
            return False,'SMCIPMITool and ipmitool package not found'
        for bmc_cmd_do in bmc_cmd:
            rc=self.run_cmd(bmc_cmd_do,path=path,retry=retry,timeout=timeout,ipmi=ipmi,return_code=return_code)
            if rc[0]:
                # If change this rule then node_state will mixed up
                return True,rc[1][1]
        return False,'Timeout'

    def reset(self,cmd,ipmi={},retry=0):
        rc=self.do_cmd('ipmi reset',ipmi=ipmi,retry=retry)
        return rc[0]

    def get_mac(self,ipmi={}):
        ipmi_mac=self.root.bmc.ipmi_mac.GET(default=None)
        if ipmi_mac:
            return True,[ipmi_mac]
        rc=self.do_cmd('ipmi lan mac',ipmi=ipmi)
        if rc[0]:
            ipmi=self.ipmi_info(ipmi)
            if ipmi[0]:
                ipmi_mode=ipmi[1].get('ipmi_mode',None)
                if ipmi_mode == 'smc':
                    return True,[rc[1].lower()]
                else:
                    for ii in rc[1].split('\n'):
                        ii_a=ii.split()
                        if ii_a[0] == 'MAC' and ii_a[1] == 'Address' and ii_a[2] == ':':
                            self.root.bmc.PUT('ipmi_mac',ii_a[-1].lower(),{'readonly':True})
                            return True,[ii_a[-1].lower()]
        return False,[]

    def get_eth_mac(self,ipmi={}):
        ipmi=self.ipmi_info(ipmi)
        if ipmi[0]:
            ipmi_mode=ipmi[1].get('ipmi_mode',None)
            if ipmi_mode == 'smc':
                rc=self.do_cmd('ipmi oem summary | grep "System LAN"',ipmi=ipmi)
                if rc[0]:
                    rrc=[]
                    for ii in rc[1].split('\n'):
                        rrc.append(ii.split()[-1].lower())
                    return True,rrc
            else:
                rc=self.do_cmd('''raw 0x30 0x21 | tail -c 18 | sed "s/ /:/g"''',ipmi=ipmi)
                if rc[0]:
                    return True,[rc[1].lower()]
        return False,[]

    def dhcp(self,ipmi={}):
        ipmi=self.ipmi_info(ipmi)
        if ipmi[0] is False:
            return False,'wrong IP'
        ipmi_mode=ipmi[1].get('ipmi_mode',None)
        if ipmi_mode == 'smc':
            rc=self.do_cmd('ipmi lan dhcp',ipmi=ipmi[1])
            if rc[0]:
                return True,rc[1]
        else:
            rc=self.do_cmd('lan print',ipmi=ipmi[1])
            if rc[0]:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'IP' and ii_a[1] == 'Address' and ii_a[2] == 'Source':
                        return True,ii_a[-2]
        return False,None

    def gateway(self,ipmi={}):
        ipmi=self.ipmi_info(ipmi)
        if ipmi[0] is False:
            return False,'wrong IP'
        ipmi_mode=ipmi[1].get('ipmi_ip',None)
        if ipmi_mode == 'smc':
            rc=self.do_cmd('ipmi lan gateway',ipmi=ipmi)
            if rc[0]:
                return True,rc[1]
        else:
            rc=self.do_cmd('lan print',ipmi=ipmi)
            if rc[0]:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'Default' and ii_a[1] == 'Gateway' and ii_a[2] == 'IP':
                        return True,ii_a[-1]
        return False,None

    def netmask(self,ipmi={}):
        ipmi=self.ipmi_info(ipmi)
        if ipmi[0] is False:
            return False,'wrong IP'
        ipmi_mode=ipmi[1].get('ipmi_ip',None)
        if ipmi_mode == 'smc':
            rc=self.do_cmd('ipmi lan netmask',ipmi=ipmi)
            if rc[0]:
                return True,rc[1]
        else:
            rc=self.do_cmd('lan print',ipmi=ipmi)
            if rc[0]:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'Subnet' and ii_a[1] == 'Mask':
                        return True,ii_a[-1]
        return False,None

    def bootorder(self,mode=None,ipxe=False,persistent=False,force=False,boot_mode=['pxe','ipxe','bios','hdd']):
        for i in range(0,2):
            if mode in [None,'order']:
                rc=self.do_cmd('chassis bootparam get 5',ipmi=self.ipmi_info(ipmi_mode='ipmitool'))
                if mode == 'order':
                   if rc[0]:
                       rc=True,km.findstr(rc[1],'- Boot Device Selector : (\w.*)')[0]
            else:
                if not mode in boot_mode:
                    return False,'Unknown boot mode({})'.format(mode)
                if persistent:
                    if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                        rc=self.do_cmd(cmd='raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00',ipmi=self.ipmi_info(ipmi_mode='ipmitool'))
                    else:
                        rc=self.do_cmd('chassis bootdev {0} options=persistent'.format(mode),ipmi=self.ipmi_info(ipmi_mode='ipmitool'))
                else:
                    if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                        rc=self.do_cmd('chassis bootdev {0} options=efiboot'.format(mode),ipmi=self.ipmi_info(ipmi_mode='ipmitool'))
                    else:
                        if force and boot_mode == 'pxe':
                            rc=self.do_cmd('chassis bootparam set bootflag force_pxe'.format(mode),ipmi=self.ipmi_info(ipmi_mode='ipmitool'))
                        else:
                            rc=self.do_cmd('chassis bootdev {0}'.format(mode),ipmi=self.ipmi_info(ipmi_mode='ipmitool'))
            if rc[0]:
                return True,rc[1]
            else:
                ok,ipmi_user,ipmi_pass=self.find_user_pass()
                if ok is False:
                    return False,'Can not find working BMC user and password'
        return False,'Tiemout'

    def ping(self,ip=None,test_num=3,retry=1,wait=1,keep=0,timeout=60): # BMC is on (pinging)
        if ip is None:
            ip=self.root.bmc.ipmi_ip.GET()
        return km.ping(ip,test_num=test_num,retry=retry,wait=wait,keep=keep,log=self.log)

    def info(self,**opts): # BMC is ready(hardware is ready)
        ipmi=self.ipmi_info(opts)
        if ipmi[0] is False:
            print('%10s : %s is not IPMI IP'%("IP",ipmi[1]['ipmi_ip']))
            os._exit(1)
        print('%10s : %s'%("IP",ipmi[1]['ipmi_ip']))
        if self.ping(ipmi[1]['ipmi_ip']) is False:
            print('%10s : %s'%("Ping","Fail"))
            return False
        print('%10s : %s'%("Ping","OK"))
        print('%10s : %s'%("User",ipmi[1]['ipmi_user']))
        print('%10s : %s'%("Password",ipmi[1]['ipmi_pass']))
        ok,mac=self.get_mac(ipmi=ipmi)
        print('%10s : %s'%("Bmc Mac",'{}'.format(mac)))
        ok,eth_mac=self.get_eth_mac(ipmi=ipmi)
        if ok:
            print('%10s : %s'%("Eth Mac",'{}'.format(eth_mac)))
        print('%10s : %s'%("Power",'{}'.format(self.power('status',ipmi=ipmi)[1])))
        print('%10s : %s'%("DHCP",'{}'.format(self.dhcp(ipmi=ipmi)[1])))
        print('%10s : %s'%("Gateway",'{}'.format(self.gateway(ipmi=ipmi)[1])))
        print('%10s : %s'%("Netmask",'{}'.format(self.netmask(ipmi=ipmi)[1])))
        print('%10s : %s'%("LanMode",'{}'.format(self.lanmode()[1])))
        print('%10s : %s'%("BootOrder",'{}'.format(self.bootorder()[1])))

    def node_state(self,state='up',timeout=600,keep_up=40,interval=8, down_monitor=0,**opts): # Node state
        if keep_up >= timeout:
            timeout=int('{}'.format(keep_up)) + 30
        if down_monitor >= timeout:
            timeout=int('{}'.format(down_monitor)) + 30
        stop_func=opts.get('stop_func',None)
        stop_stop_arg=opts.get('stop_arg',{})
        ipmi_mode=opts.get('ipmi_mode',self.root.bmc.ipmi_mode.GET())
        # -: Down, +: Up, ?: Unknown sensor data, !: ipmi sensor command error
        init_time=int(datetime.datetime.now().strftime('%s'))
        up_time=0
        down_chk=False
        tmp=''
        while True:
            if stop_func and type(stop_arg) is dict:
                if stop_func(**stop_arg) is True:
                    if self.log:
                        self.log("Got STOP signal",log_level=6)
                    return False,'Got STOP signal'
            if int(datetime.datetime.now().strftime('%s')) - init_time > timeout:
                break
            krc=self.do_cmd('ipmi sensor',ipmi=self.ipmi_info(ipmi_mode=ipmi_mode))
            if krc[0]:
                for ii in krc[1].split('\n'):
                    ii_a=ii.split('|')
                    find=''
                    if ipmi_mode == 'smc' and len(ii_a) > 2:
                        find=ii_a[1].strip()
                        tmp=ii_a[2].strip()
                    elif len(ii_a) > 4:
                        find=ii_a[0].strip()
                        tmp=ii_a[4].strip()
                    if 'Temp' in find and ('CPU' in find or 'System' in find):
                        if tmp == 'No Reading':
                            if keep_up > 0 and up_time > 0:
                                up_time=0
                            km.logging('?',log=self.log,direct=True,log_level=2)
                        elif tmp in ['N/A','Disabled','0C/32F']:
                            down_chk=True
                            if state == 'down': 
                                km.logging(' ',log=self.log,log_level=2)
                                return True,'down'
                            if keep_up > 0 and up_time > 0:
                                up_time=0
                            km.logging('-',log=self.log,direct=True,log_level=2)
                        else:
                            if state == 'up': 
                                if keep_up > 0:
                                     if up_time == 0:
                                         up_time=int(datetime.datetime.now().strftime('%s'))
                                     if int(datetime.datetime.now().strftime('%s')) - up_time > keep_up:
                                         if down_monitor and down_chk is False: #check down but not down then keep check down
                                             continue
                                         km.logging(' ',log=self.log,log_level=2)
                                         return True,'up'
                                else:
                                     if down_monitor and down_chk is False: #check down but not down then keep check down
                                         continue
                                     km.logging(' ',log=self.log,log_level=2)
                                     return True,'up'
                            km.logging('+',log=self.log,direct=True,log_level=2)
            else:
                if keep_up > 0 and up_time > 0:
                    up_time=0
                km.logging('!',log=self.log,direct=True,log_level=2)
            sys.stdout.flush()
            time.sleep(interval)
        km.logging(' ',log=self.log,log_level=2)
        if tmp == 'No Reading':
            self.root.bmc.UPDATE({'error':{'sensor':{int(datetime.datetime.now().strftime('%s')):tmp}}})
        return False,'timeout'

    def is_up(self,ipmi={},timeout=1200,keep_up=40,interval=8): # Node state
        return self.node_state(state='up',ipmi=ipmi,timeout=timeout,keep_up=keep_up,interval=interval) # Node state

    def is_down(self,ipmi={},timeout=240,interval=8): # Node state
        return self.node_state(state='down',ipmi=ipmi,timeout=timeout,keep_up=0,interval=interval) # Node state

    def power_handle(self,cmd='status',retry=0,ipmi={},boot_mode=None,order=False,ipxe=False,log_file=None,log=None,force=False,mode=None,verify=True,keep_up=20,timeout=1200,lanmode=None):
        ipmi=self.ipmi_info(ipmi)
        if ipmi[0] is False:
            return False,'wrong IP'
        if cmd == 'status':
            return self.power('status',ipmi=ipmi,verify=verify)
        if boot_mode:
            km.logging('Set Boot mode to {}\n'.format(boot_mode),log_level=3)
            if ipxe in ['on','On',True,'True']:
                ipxe=True
            else:
                ipxe=False
            if boot_mode == 'ipxe':
                ipxe=True
                boot_mode='pxe'
            for ii in range(0,retry+1):
                # Find ipmi information
                ipmi_ok,ipmi_ip,ipmi_user,ipmi_pass,ipmi_mode=self.ipmi_info(ipmi,rf='tuple')
                km.set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,persistent=order,ipxe=ipxe,log_file=log_file,log=log,force=force)
                boot_mode_state=km.get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
                if (boot_mode == 'pxe' and boot_mode_state[0] is not False and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
                    break
                km.logging(' retry boot mode set {} (ipxe:{},force:{})[{}/5]'.format(boot_mode,ipxe,order,ii),log=self.log,log_level=6)
                time.sleep(2)
        return self.power(cmd,ipmi=ipmi,retry=retry,verify=verify,timeout=timeout,keep_up=keep_up,lanmode=lanmode)

    def power(self,cmd,ipmi={},retry=0,verify=True,timeout=1200,keep_up=40,lan_mode=None):
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

        power_mode=self.root.bmc.power_mode.GET(default=[])
        if cmd not in ['status','off_on'] + list(power_mode):
            return False,'Unknown command({})'.format(cmd)

        ipmi=self.ipmi_info(ipmi)
        if ipmi[0] is False:
            return False,'wrong IP'
        power_step=len(power_mode[cmd])-1
        for ii in range(1,int(retry)+2):
            checked_lanmode=None
            init_rc=self.do_cmd('ipmi power status',ipmi=ipmi)
            if verify is False or cmd == 'status':
                if init_rc[0]:
                    if cmd == 'status':
                        return True,init_rc[1],ii
                    return True,rc[1],ii
                time.sleep(3)
                continue
            # keep command
            init_status=init_rc[1].split()[-1]
            km.logging('Power {} at {} (try:{}/{}) (limit:{} sec)'.format(cmd,ipmi['ipmi_ip'],ii,retry+1,self.root.bmc.timeout.GET()),log=self.log,log_level=3)
            chk=1
            for rr in list(power_mode[cmd]):
                verify_status=rr.split(' ')[-1]
                if chk == 1 and init_rc[0] and init_status == verify_status:
                    if chk == len(power_mode[cmd]):
                        return True,verify_status,0
                    chk+=1
                    continue
                # BMC Lan mode Checkup before power on/cycle/reset
                if checked_lanmode is None and mode and verify_status in ['on','reset','cycle']:
                   checked_lanmode=lanmode_check(lan_mode)

                if verify_status in ['reset','cycle']:
                     if self.is_down(ipmi=ipmi)[0]:
                         km.logging(' ! can not {} the power at {} status'.format(verify_status,sys_status[1]),log=self.log,log_level=6)
                         return [False,'can not {} at {} status'.format(verify_status,sys_status[1])]
                rc=self.do_cmd(rr,ipmi=ipmi,retry=retry)
                if rc[0] in [0,True]:
                    km.logging(' + Do power {}'.format(verify_status),log=self.log,log_level=6)
                    if verify_status in ['reset','cycle']:
                        verify_status='on'
                        time.sleep(10)
                else:
                    km.logging(' ! power {} fail'.format(verify_status),log=self.log,log_level=6)
                    time.sleep(5)
                    break
                if verify_status == 'on':
                    if self.is_up(ipmi=ipmi,timeout=timeout,keep_up=keep_up)[0]:
                        if chk == len(power_mode[cmd]):
                            return True,'on',ii
                    time.sleep(3)
                elif verify_status == 'off':
                    if self.is_down(ipmi=ipmi)[0]:
                        if chk == len(power_mode[cmd]):
                            return True,'off',ii
                    time.sleep(3)
                chk+=1
            time.sleep(3)
        return False,'time out',ii

    def lanmode(self,mode=None):
        if self.smc_file is None:
            if self.log:
                self.log(' - SMCIPMITool({}) not found'.format(self.smc_file),log_level=5)
                return False,'SMCIPMITool not found'
        if mode in [0,1,2,'0','1','2']:
            bmc_cmd=self.bmc_cmd("""ipmi oem lani {}""".format(mode),ipmi_mode='smc')
        else:
            bmc_cmd=self.bmc_cmd("""ipmi oem lani""",ipmi_mode='smc')
        lanmode_info=self.run_cmd(bmc_cmd[1],path=self.root.bmc.tool_path.GET(),ipmi=self.ipmi_info(ipmi_mode='smc'),return_code={'ok':[144]})
        if lanmode_info[0]:
            a=km.findstr(lanmode_info[1][1],'Current LAN interface is \[ (\w.*) \]')
            if len(a) == 1:
                return True,a[0]
        return False,None

if __name__ == "__main__":
    import kDict
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

    dest_ip='172.16.219.108'
    tool_path='/django/sumViewer.5/tools'
    ipmi_user='ADMIN'
    ipmi_pass='ADMIN'
    if len(sys.argv) == 5:
        dest_ip=sys.argv[1]
        tool_path=sys.argv[2]
        ipmi_user=sys.argv[3]
        ipmi_pass=sys.argv[4]
    elif len(sys.argv) == 2 and sys.argv[1] in ['help','-h','--help']:
        print('{} <ipmi ip> <bin dir> <ipmi_user> <ipmi_pass>'.format(sys.argv[0]))
        os._exit(1)

    print('Test at {}'.format(dest_ip))
    root=kDict.kDict()
    bmc=BMC(root,ipmi_ip=dest_ip,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog,tool_path=tool_path)
    #bmc=BMC(root,ipmi_ip='172.16.220.135',ipmi_user='ADMIN',ipmi_pass='ADMIN',test_pass=['ADMIN','Admin'],test_user=['ADMIN','Admin'],timeout=1800,log=KLog)
    print(bmc.power_handle(cmd='status'))
    #print(bmc.power_handle(cmd='off_on'))
    print(bmc.info())

