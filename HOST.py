#Kage Park
import socket
from klib.MODULE import MODULE
MODULE().Import('from klib.DEV import *')
MODULE().Import('from klib.SHELL import SHELL')
MODULE().Import('from klib.IS import IS')

class HOST:
    def __init__(self):
        pass
    def Name(self):
        return socket.gethostname()

    def Ip(self,ifname=None,mac=None):
        if ifname or mac:
            if mac:
                ifname=get_dev_name_from_mac(mac)
            return self.NetIp(ifname)
        else:
            ifname=get_dev_name_from_mac()
            if ifname:
                ip=self.NetIp(ifname)
                if ip:
                    return ip
            return socket.gethostbyname(socket.gethostname())

    def IpmiIp(self):
        return SHELL().Run('''ipmitool lan print 2>/dev/null| grep "IP Address" | grep -v Source | awk '{print $4}' ''')

    def IpmiMac(self):
        return SHELL().Run(""" ipmitool lan print 2>/dev/null | grep "MAC Address" | awk """ + """ '{print $4}' """)

    def DevMac(self,ifname):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
            return ':'.join(['%02x' % ord(char) for char in info[18:24]])
        except:
            return

    def Mac(self,ip=None,dev=None):
        if IS(ip).Ipv4():
            dev_info=get_net_device()
            for dev in dev_info.keys():
                if self.NetIp(dev) == ip:
                    return dev_info[dev]['mac']
        elif dev:
            return self.DevMac(dev)
        else:
            #return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
            return CONVERT('%012x' % uuid.getnode()).Str2Mac()

    def DevName(self,mac=None):
        if mac is None:
            mac=self.Mac()
        net_dir='/sys/class/net'
        if isinstance(mac,str) and os.path.isdir(net_dir):
            dirpath,dirnames,filenames = list(os.walk(net_dir))[0]
            for dev in dirnames:
                fmac=cat('{}/{}/address'.format(dirpath,dev),no_end_newline=True)
                if isinstance(fmac,str) and fmac.strip().lower() == mac.lower():
                    return dev

    def NetIP(ifname):
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

    def Info(self):
        return {
         'host_name':self.Name(),
         'host_ip':self.Ip(),
         'host_mac':self.Mac(),
         'ipmi_ip':self.IpmiIp()[1],
         'ipmi_mac':self.IpmiMac()[1],
         }

