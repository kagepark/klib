# Kage Park
# Inteligent BMC Tool

import os
from distutils.spawn import find_executable
import datetime
import time
import sys
import kmisc as km

class BMC:
    def __init__(self,root,ipmi_ip=None,ipmi_user=None,ipmi_pass=None,uniq_ipmi_pass=None,log=None,timeout=1800,tool_path=None,mode='ipmitool',smc_file=None,test_user=[],test_pass=[]):
        # Initial Dictionary
        self.root=root
        self.test_user=['ADMIN','Admin']
        self.test_pass=['ADMIN','Admin']
        # If need update initial data then update
        self.root.log.PUT('write',log,{'readonly':True})
        self.log=self.root.log.write.GET()
        self.root.bmc.PUT('timeout',timeout,{'readonly':True})
        self.root.bmc.PUT('power_mode',{'on':['chassis power on'],'off':['chassis power off'],'reset':['chassis power reset'],'off_on':['chassis power off','chassis power on'],'on_off':['chassis power on','chassis power off'],'cycle':['chassis power cycle'],'status':['chassis power status']},{'readonly':True})
        self.root.bmc.PUT('ipmi_ip',ipmi_ip)
        self.root.bmc.PUT('ipmi_user',ipmi_user,{'readonly':True})
        self.root.bmc.PUT('ipmi_pass',ipmi_pass,{'readonly':True})
        for ii in test_user:
            if ii not in self.test_user:
                self.test_user.append(ii)
        for ii in test_pass:
            if ii not in self.test_pass:
                self.test_pass.append(ii)
        if self.root.bmc.ipmi_user.GET() in self.test_user:
            self.test_user.remove(self.root.bmc.ipmi_user.GET())
        self.root.bmc.PUT('test_user',[self.root.bmc.ipmi_user.GET()]+self.test_user)
        if uniq_ipmi_pass:
            self.root.bmc.PUT('uniq_pass',uniq_ipmi_pass,{'readonly':True})
            if uniq_ipmi_pass in self.test_pass:
                self.test_pass.remove(uniq_ipmi_pass)
            self.test_pass=[uniq_ipmi_pass]+self.test_pass
        if self.root.bmc.ipmi_pass.GET() in self.test_pass:
            self.test_pass.remove(self.root.bmc.ipmi_pass.GET())
        self.root.bmc.PUT('test_pass',[self.root.bmc.ipmi_pass.GET()]+self.test_pass)
        self.root.bmc.PUT('tool_path',tool_path,{'readonly':True})
        self.root.bmc.PUT('smc_file',smc_file,{'readonly':True})
        self.smc_file='/'.join(self.root.bmc.LIST(['tool_path','smc_file']))
        self.ipmitool=True
        if os.path.isfile(self.smc_file) is False:
            self.smc_file=None
            if mode == 'smc':
                 if self.log:
                     self.log(' {} not found. So it changed mode to ipmi'.format(self.smc_file),log_level=1)
                     self.log(' go to https://www.supermicro.com/SwDownload/SwSelect_Free.aspx?cat=IPMI and download SMCIPMITool package',log_level=1)
        if find_executable('ipmitool') is False:
             self.ipmitool=False
             if self.log:
                 self.log(' ipmitool package not found',log_level=1)
                 self.log(' Install ipmitool package(yum install ipmitool)',log_level=1)
        if self.root.bmc.mode.PROPER('readonly'):
            self.root.bmc.mode.PROPER('readonly',False)
        if self.smc_file and self.ipmitool:
            if mode == 'smc':
                self.root.bmc.PUT('mode',['smc','ipmitool'],{'readonly':True})
            else:
                self.root.bmc.PUT('mode',['ipmitool','smc'],{'readonly':True})
        elif self.ipmitool:
            self.root.bmc.PUT('mode',['ipmitool'],{'readonly':True})
        elif self.smc_file:
            self.root.bmc.PUT('mode',['smc'],{'readonly':True})
        else:
            print("SMCIPMITool and ipmitool not found")
            os._exit(1)

    def bmc_cmd(self,cmd,**opts):
        ipmi_ip=opts.get('ipmi_ip',None)
        if ipmi_ip is None:
            ipmi_ip=self.root.bmc.ipmi_ip.GET()
        ipmi_user=opts.get('ipmi_user',None)
        if ipmi_user is None:
            ipmi_user=self.root.bmc.ipmi_user.GET()
        ipmi_pass=opts.get('ipmi_pass',None)
        if ipmi_pass is None:
            ipmi_pass=self.root.bmc.ipmi_pass.GET()
        mode=opts.get('mode',None)
        option=opts.get('option','lanplus')
        cmd_a=cmd.split()
        if isinstance(mode,list):
            mode=mode[0]
        if mode == 'smc':
            if self.smc_file is None:
                return False,'SMCIPMITool file not found'
            if km.value_check(cmd_a,'chassis',0) and km.value_check(cmd_a,'power',1):
                cmd_a[0] == 'ipmi'
            elif km.value_check(cmd_a,'mc',0) and km.value_check(cmd_a,'reset',1) and km.value_check(cmd_a,'cold',2):
                cmd_a=['ipmi','reset']
            elif km.value_check(cmd_a,'lan',0) and km.value_check(cmd_a,'print',1):
                cmd_a=['ipmi','lan','mac']
            elif km.value_check(cmd_a,'sdr',0) and km.value_check(cmd_a,'Temperature',2):
                cmd_a=['ipmi','sensor']
            return True,'''sudo java -jar {} {} {} '{}' {}'''.format(self.smc_file,ipmi_ip,ipmi_user,ipmi_pass,' '.join(cmd_a))
        elif mode in ['ipmitool',None]:
            if self.ipmitool is False:
                return False,'ipmitool package not found'
            if km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'power',1) and km.value_get(cmd_a,2) in self.root.bmc.power_mode.GET():
                cmd_a[0] = 'chassis'
            elif km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'reset',1):
                cmd_a=['mc','reset','cold']
            elif km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'lan',1) and km.value_check(cmd_a,'mac',2):
                cmd_a=['lan','print']
            elif km.value_check(cmd_a,'ipmi',0) and km.value_check(cmd_a,'sensor',1):
                cmd_a=['sdr','type','Temperature']
            return True,'''ipmitool -I {} -H {} -U {} -P '{}' {}'''.format(option,ipmi_ip,ipmi_user,ipmi_pass,' '.join(cmd_a))
        return False,'''Unknown mode({})'''.format(mode)

    def check_passwd(self,**opts):
        ipmi_user=opts.get('ipmi_user',self.root.bmc.ipmi_user.GET())
        ipmi_pass=opts.get('ipmi_pass',self.root.bmc.ipmi_pass.GET())
        bmc_cmd=self.bmc_cmd('ipmi power status',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass)
        if bmc_cmd[0]:
            rc=km.rshell(bmc_cmd[1])
            if rc[0] == 0:
                return True
        return False

    def find_user_pass(self,ipmi_user=None,ipmi_pass=None,mode=None):
        test_user_a=self.root.bmc.test_user.GET()[:]
        test_pass_a=self.root.bmc.test_pass.GET()[:]
        default_range=3
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
                        return True,uu,pp
        if self.log:
            self.log(' Can not find working BMC User and password',log_level=1)
        return False,None,None
###########################

    def recover_user_pass(self,cur_user=None,cur_pass=None):
        if self.smc_file is None:
            if self.log:
                self.log(' - {} not found'.format(self.smc_file))
            return False,cur_user,cur_pass
        ok,ipmi_user,ipmi_pass=self.find_user_pass(ipmi_user=cur_user,ipmi_pass=cur_pass)
        if ok is False:
            if self.log:
                self.log(' - Can not find working User and Password (Input:({},{}), ({},{}))'.format(cur_user,cur_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),log_level=1)
                return False,cur_user,cur_pass
        if self.root.bmc.ipmi_user.CHECK(cur_user) is False or self.root.bmc.ipmi_pass.CHECK(cur_pass) is False:
            if self.log:
                self.log(' - Found New BMC Info from User({}) and Password({}) to User({}) and Password({})'.format(cur_user,cur_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),log_level=1)

        if ipmi_user and ipmi_pass:
            if ipmi_user == self.root.bmc.ipmi_user.GET() and ipmi_pass == self.root.bmc.ipmi_pass.GET():
                if self.log:
                    self.log(' - Same user and passwrd. Do not need recover',log_level=6)
                return True,ipmi_user,ipmi_pass
            if ipmi_user == self.root.bmc.ipmi_user.GET():
                #SMCIPMITool.jar IP ID PASS user setpwd 2 <New Pass>
                bmc_cmd=self.bmc_cmd("""user setpwd 2 '{}'""".format(self.root.bmc.ipmi_pass.GET()),ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode='smc')
            else:
                #SMCIPMITool.jar IP ID PASS user add 2 <New User> <New Pass> 4
                bmc_cmd=self.bmc_cmd("""user add 2 {} '{}' 4""".format(self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode='smc')
            if bmc_cmd[0] is False:
                return bmc_cmd
            rc=km.rshell(bmc_cmd[1])
            if rc[0] == 0:
                if self.log:
                    self.log(' - Recovered BMC: from User({}) and Password({}) to User({}) and Password({})'.format(ipmi_user,ipmi_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()),log_level=6)
                return True,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET()
            else:
                if self.log:
                    log(' - Not support {}. Looks need more length. So Try again with Super123'.format(ipmi_pass),log_level=6)
                if ipmi_user == self.root.bmc.ipmi_user.GET():
                    bmc_cmd=self.smc_cmd("""user setpwd 2 Super123""",ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode='smc')
                else:
                    bmc_cmd=self.smc_cmd("""user add 2 {} Super123 4""".format(self.root.bmc.ipmi_user.GET()),ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode='smc')
                rc=km.rshell(smc_cmd[1])
                if rc[0] == 0:
                    if self.log:
                        self.log(' - Recovered BMC with Super123: from User({}) and Password({}) to User({}) and Password(Super123)'.format(ipmi_user,ipmi_pass,self.root.bmc.ipmi_user.GET()),log_level=6)
                    return True,self.root.bmc.ipmi_user.GET(),'Super123'
                else:
                    if self.log:
                        self.log(' - Recover BMC ERROR !!! : from User({}) and Password ({}) to User({}) and Password({})\n{}'.format(ipmi_user,ipmi_pass,self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET(),rc),log_level=6)
                    return False,ipmi_user,ipmi_pass
        else:
            if self.log:
                self.log(' - Recover BMC ERROR !!! : Can not find acceptable user and password. (current user({}), password({}))'.format(ipmi_user,ipmi_pass),log_level=6)
            return False,ipmi_user,ipmi_pass

    def do_cmd(self,cmd,path=None,ipmi_user=None,ipmi_pass=None,retry=2,mode=None):
        def get_bmc_cmd(ipmi_user,ipmi_pass,mode):
            bmc_cmd=[]
            if mode in ['all','*']:
                for ii in self.bmc.mode.GET():
                    chk_cmd=self.bmc_cmd(cmd,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=ii)
                    if chk_cmd[0]:
                        bmc_cmd.append(chk_cmd[1])
            else:
                chk_cmd=self.bmc_cmd(cmd,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode)
                if chk_cmd[0]:
                    bmc_cmd.append(chk_cmd[1])
            return bmc_cmd

        bmc_cmd=get_bmc_cmd(ipmi_user,ipmi_pass,mode)
        if len(bmc_cmd) == 0:
            return False,'SMCIPMITool and ipmitool package not found'
        for bmc_cmd_do in bmc_cmd:
            for i in range(0,retry):
                if path:
                    rc=km.rshell(bmc_cmd_do,path=path)
                else:
                    rc=km.rshell(bmc_cmd_do)
                if rc[0] == 0:
                    return True,rc[1]
                else:
                    ok,ipmi_user,ipmi_pass=self.find_user_pass(ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode)
                    if ok is True:
                        bmc_cmd=get_bmc_cmd(ipmi_user,ipmi_pass,mode)
                    else:
                        return False,'Can not find working IPMI USER and PASSWORD'
        return False,'Timeout'

    def reset(self,cmd,mode=None,retry=2):
        rc=self.do_cmd('ipmi reset',mode=mode,retry=retry)
        return rc[0]

    def get_mac(self,mode=None):
        if mode is None:
            mode=self.mode
        rc=self.do_cmd('ipmi lan mac',mode=mode)
        if rc[0]:
            if mode == 'smc':
                return True,[rc[1].lower()]
            else:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'MAC' and ii_a[1] == 'Address' and ii_a[2] == ':':
                        return True,[ii_a[-1].lower()]
        return False,[]

    def get_eth_mac(self,mode=None):
        if mode is None:
            mode=self.root.bmc.mode.GET(default=None)
        if mode == 'smc':
            rc=self.do_cmd('ipmi oem summary | grep "System LAN"',mode=mode)
            if rc[0]:
                rrc=[]
                for ii in rc[1].split('\n'):
                    rrc.append(ii.split()[-1].lower())
                return True,rrc
        else:
            rc=self.do_cmd('''raw 0x30 0x21 | tail -c 18 | sed "s/ /:/g"''',mode=mode)
            if rc[0]:
                return True,[rc[1].lower()]
        return False,[]

    def dhcp(self,mode=None):
        if mode is None:
            mode=self.root.bmc.mode.GET(default=None)
        if mode == 'smc':
            rc=self.do_cmd('ipmi lan dhcp',mode=mode)
            if rc[0]:
                return True,rc[1]
        else:
            rc=self.do_cmd('lan print',mode=mode)
            if rc[0]:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'IP' and ii_a[1] == 'Address' and ii_a[2] == 'Source':
                        return True,ii_a[-2]
        return False,None

    def gateway(self,mode=None):
        if mode is None:
            mode=self.root.bmc.mode.GET(default=None)
        if mode == 'smc':
            rc=self.do_cmd('ipmi lan gateway',mode=mode)
            if rc[0]:
                return True,rc[1]
        else:
            rc=self.do_cmd('lan print',mode=mode)
            if rc[0]:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'Default' and ii_a[1] == 'Gateway' and ii_a[2] == 'IP':
                        return True,ii_a[-1]
        return False,None

    def netmask(self,mode=None):
        if mode is None:
            mode=self.root.bmc.mode.GET(default=None)
        if mode == 'smc':
            rc=self.do_cmd('ipmi lan netmask',mode=mode)
            if rc[0]:
                return True,rc[1]
        else:
            rc=self.do_cmd('lan print',mode=mode)
            if rc[0]:
                for ii in rc[1].split('\n'):
                    ii_a=ii.split()
                    if ii_a[0] == 'Subnet' and ii_a[1] == 'Mask':
                        return True,ii_a[-1]
        return False,None

    def bootorder(self,mode=None,ipxe=False,persistent=False,force=False,boot_mode=['pxe','ipxe','bios','hdd']):
        for i in range(0,2):
            if mode is None:
#                rc=km.get_boot_mode(self.root.bmc.ipmi_ip.GET(),self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET(),log=self.log)
                rc=self.do_cmd('chassis bootparam get 5',mode='ipmitool')
            else:
                #rc=km.set_boot_mode(self.root.bmc.ipmi_ip.GET(),self.root.bmc.ipmi_user.GET(),self.root.bmc.ipmi_pass.GET(),state,ipxe=ipxe,persistent=persistent,log=self.log)
                if not mode in boot_mode:
                    return False,'Unknown boot mode({})'.format(mode)
                if persistent:
                    if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                        rc=self.do_cmd(cmd='raw 0x00 0x08 0x05 0xe0 0x04 0x00 0x00 0x00',mode='ipmitool')
                    else:
                        rc=self.do_cmd('chassis bootdev {0} options=persistent'.format(mode),mode='ipmitool')
                else:
                    if mode == 'pxe' and ipxe in ['on','ON','On',True,'True']:
                        rc=self.do_cmd('chassis bootdev {0} options=efiboot'.format(mode),mode='ipmitool')
                    else:
                        if force and boot_mode == 'pxe':
                            rc=self.do_cmd('chassis bootparam set bootflag force_pxe'.format(mode),mode='ipmitool')
                        else:
                            rc=self.do_cmd('chassis bootdev {0}'.format(mode),mode='ipmitool')
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

    def info(self,ip=None,ipmi_user=None,ipmi_pass=None,mode=None): # BMC is ready(hardware is ready)
        if ip is None:
            ip=self.root.bmc.ipmi_ip.GET()
        if ipmi_user is None:
            ipmi_user=self.root.bmc.ipmi_user.GET()
        if ipmi_pass is None:
            ipmi_pass=self.root.bmc.ipmi_pass.GET()
        if mode is None:
            mode=self.root.bmc.mode.GET()
        print('%10s : %s'%("IP",ip))
        if self.ping(ip) is False:
            print('%10s : %s'%("Ping","Fail"))
            return False
        print('%10s : %s'%("Ping","OK"))
        ok,ipmi_user,ipmi_pass=self.find_user_pass(ipmi_user,ipmi_pass,mode=mode)
        if ok:
            if ipmi_user == self.root.bmc.ipmi_user.GET():
                print('%10s : %s'%("User",ipmi_user))
            else:
                print('%10s : %s => %s'%("User",self.root.bmc.ipmi_user.GET(),ipmi_user))
            if ipmi_pass == self.root.bmc.ipmi_pass.GET():
                print('%10s : %s'%("Password",ipmi_pass))
            else:
                print('%10s : %s => %s'%("Password",self.root.bmc.ipmi_pass.GET(),ipmi_pass))
        else:
            print('%10s : %s'%("User",ipmi_user))
            print('%10s : %s'%("Password",ipmi_pass))
            print('But, can not access with above user and password')
            return False
        ok,mac=self.get_mac(mode=mode)
        print('%10s : %s'%("Bmc Mac",'{}'.format(mac)))
        ok,eth_mac=self.get_eth_mac(mode=mode)
        if ok:
            print('%10s : %s'%("Eth Mac",'{}'.format(eth_mac)))
        print('%10s : %s'%("Power",'{}'.format(self.power('status',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass)[1])))
        print('%10s : %s'%("DHCP",'{}'.format(self.dhcp(mode=mode)[1])))
        print('%10s : %s'%("Gateway",'{}'.format(self.gateway(mode=mode)[1])))
        print('%10s : %s'%("Netmask",'{}'.format(self.netmask(mode=mode)[1])))
        print('%10s : %s'%("BootOrder",'{}'.format(self.bootorder()[1])))

    def node_state(self,state='up',ipmi_user=None,ipmi_pass=None,mode=None,timeout=600,keep_up=40,interval=8, down_monitor=0,**opts): # Node state
        if keep_up >= timeout:
            timeout=int('{}'.format(keep_up)) + 30
        if down_monitor >= timeout:
            timeout=int('{}'.format(down_monitor)) + 30
        stop_func=opts.get('stop_func',None)
        stop_stop_arg=opts.get('stop_arg',{})
        # *: Down, +: Up, -: Get error
        init_time=int(datetime.datetime.now().strftime('%s'))
        up_time=0
        down_chk=False
        while True:
            if stop_func and type(stop_arg) is dict:
                if stop_func(**stop_arg) is True:
                    if self.log:
                        self.log("Got STOP signal",log_level=6)
                    return False,'Got STOP signal'
            if int(datetime.datetime.now().strftime('%s')) - init_time > timeout:
                break
            bmc_cmd=self.bmc_cmd('ipmi sensor',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode)
            if bmc_cmd[0] is False:
                return bmc_cmd 
            krc=km.rshell(bmc_cmd[1])
            if krc[0] == 0:
                for ii in krc[1].split('\n'):
                    ii_a=ii.split('|')
                    find=''
                    if mode == 'smc' and len(ii_a) > 2:
                        find=ii_a[1].strip()
                        tmp=ii_a[2].strip()
                    elif len(ii_a) > 4:
                        find=ii_a[0].strip()
                        tmp=ii_a[4].strip()
                    if 'Temp' in find and ('CPU' in find or 'System' in find):
                        if tmp == 'No Reading':
                            if keep_up > 0 and up_time > 0:
                                up_time=0
                            if self.log:
                                self.log('?',direct=True,log_level=2) # Unknown state
                            else:
                                sys.stdout.write('?')
                        elif tmp in ['N/A','Disabled','0C/32F']:
                            down_chk=True
                            if state == 'down': 
                                return True,'down'
                            if keep_up > 0 and up_time > 0:
                                up_time=0
                            if self.log:
                                self.log('-',direct=True,log_level=2) # Down
                            else:
                                sys.stdout.write('-')
                        else:
                            if state == 'up': 
                                if keep_up > 0:
                                     if up_time == 0:
                                         up_time=int(datetime.datetime.now().strftime('%s'))
                                     if int(datetime.datetime.now().strftime('%s')) - up_time > keep_up:
                                         if down_monitor and down_chk is False: #check down but not down then keep check down
                                             continue
                                         return True,'up'
                                else:
                                     if down_monitor and down_chk is False: #check down but not down then keep check down
                                         continue
                                     return True,'up'
                            if self.log:
                                self.log('+',direct=True,log_level=2) # Up
                            else:
                                sys.stdout.write('+')
            else:
                if keep_up > 0 and up_time > 0:
                    up_time=0
                if self.log:
                    self.log('!',direct=True,log_level=2) # Command Error
                else:
                    sys.stdout.write('!') 
                ok,ipmi_user,ipmi_pass=self.find_user_pass(ipmi_user,ipmi_pass,mode=mode)
            sys.stdout.flush()
            time.sleep(interval)
        return False,'timeout'

    def is_up(self,ipmi_user=None,ipmi_pass=None,mode=None,timeout=1200,keep_up=40,interval=8): # Node state
        return self.node_state(state='up',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode,timeout=timeout,keep_up=keep_up,interval=interval) # Node state

    def is_down(self,ipmi_user=None,ipmi_pass=None,mode=None,timeout=240,interval=8): # Node state
        return self.node_state(state='down',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode,timeout=timeout,keep_up=0,interval=interval) # Node state

    def power_handle(self,cmd='status',retry=2,ipmi_user=None,ipmi_pass=None,boot_mode=None,order=False,ipxe=False,log_file=None,log=None,force=False,mode=None,verify=True):
        if ipmi_user is None:
            ipmi_user=self.root.bmc.ipmi_user.GET()
        if ipmi_pass is None:
            ipmi_pass=self.root.bmc.ipmi_pass.GET()
        if cmd == 'status':
            return self.power('status',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode,verify=verify)
        if boot_mode:
            sys.stdout.write('Set Boot mode to {}\n'.format(boot_mode))
            sys.stdout.flush()
            if ipxe in ['on','On',True,'True']:
                ipxe=True
            else:
                ipxe=False
            if boot_mode == 'ipxe':
                ipxe=True
                boot_mode='pxe'
            for ii in range(0,retry):
                km.set_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,boot_mode,persistent=order,ipxe=ipxe,log_file=log_file,log=log,force=force)
                boot_mode_state=km.get_boot_mode(ipmi_ip,ipmi_user,ipmi_pass,log_file=log_file,log=log)
                if (boot_mode == 'pxe' and boot_mode_state[0] is not False and 'PXE' in boot_mode_state[0]) and ipxe == boot_mode_state[1] and order == boot_mode_state[2]:
                    break
                if self.log:
                     self.log(' retry boot mode set {} (ipxe:{},force:{})[{}/5]'.format(boot_mode,ipxe,order,ii),log_level=6)
                else:
                     print(' retry boot mode set {} (ipxe:{},force:{})[{}/5]'.format(boot_mode,ipxe,order,ii))
                time.sleep(2)
        sys.stdout.write('Do power {} '.format(cmd))
        sys.stdout.flush()
        return self.power(cmd,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,retry=retry,mode=mode,verify=verify)

    def power(self,cmd,ipmi_user=None,ipmi_pass=None,retry=2,verify=True,mode=None):
        power_mode=self.root.bmc.power_mode.GET()
        if cmd not in ['status','off_on'] + list(power_mode):
            return False,'Unknown command({})'.format(cmd)

        if verify is False or cmd == 'status':
            rc=self.do_cmd('ipmi power {}'.format(cmd),ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode,retry=retry)
            if cmd == 'status':
                return rc[1]
            return rc[0]

        power_step=len(power_mode[cmd])-1
        for ii in range(1,int(retry)+1):
            if self.log:
                 self.log('Power {} at {} (try:{}/{})'.format(cmd,self.root.bmc.ipmi_ip.GET(),ii,retry),log_level=6)
            else:
                 print('Power {} at {} (try:{}/{})'.format(cmd,self.root.bmc.ipmi_ip.GET(),ii,retry))
            init_rc=self.do_cmd('ipmi power status',ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode)
            init_status=init_rc[1].split()[-1]
            chk=1
            for rr in list(power_mode[cmd]):
                verify_status=rr.split(' ')[-1]
                if chk == 1 and init_rc[0] and init_status == verify_status:
                    if chk == len(power_mode[cmd]):
                        return [True,verify_status,0]
                    chk+=1
                    continue
                if verify_status in ['reset','cycle']:
                     if self.is_down(ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode)[0]:
                         if self.log:
                             self.log(' ! can not {} the power at {} status'.format(verify_status,sys_status[1]),log_level=6)
                         else:
                             print(' ! can not {} the power at {} status'.format(verify_status,sys_status[1]))
                         return [False,'can not {} at {} status'.format(verify_status,sys_status[1])]
                rc=self.do_cmd(rr,ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode,retry=retry)
                if rc[0] in [0,True]:
                    if self.log:
                        self.log(' + Do power {}'.format(verify_status),log_level=6)
                    else:
                        print(' + Do power {} '.format(verify_status))
                    if verify_status in ['reset','cycle']:
                        verify_status='on'
                        time.sleep(10)
                else:
                    if self.log:
                        self.log(' ! power {} fail'.format(verify_status),log_level=6)
                    else:
                        print(' ! power {} fail'.format(verify_status))
                    time.sleep(5)
                    break
                if verify_status == 'on':
                    if self.is_up(ipmi_user=ipmi_user,ipmi_pass=ipmi_pass,mode=mode)[0]:
                        if chk == len(power_mode[cmd]):
                            return [True,'on',ii]
                    time.sleep(3)
                elif verify_status == 'off':
                    if self.is_down(ipmi_user=ipmi_user,ipmi_pass=ipmi_pass)[0]:
                        if chk == len(power_mode[cmd]):
                            return [True,'off',ii]
                    time.sleep(3)
                chk+=1
            time.sleep(3)
        return [False,'time out',ii]

