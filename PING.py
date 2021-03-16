#Kage Park
import socket
from klib.TIME import TIME
from klib.IS import IS
from klib.SHELL import SHELL

def ping(host,count=3,interval=1,keep_good=0, timeout=60,lost_mon=False,log=None,stop_func=None,log_format='.',cancel_func=None):
    ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris. From /usr/include/linux/icmp.h;
    ICMP_CODE = socket.getprotobyname('icmp')
    ERROR_DESCR = {
        1: ' - Note that ICMP messages can only be '
           'sent from processes running as root.',
        10013: ' - Note that ICMP messages can only be sent by'
               ' users or processes with administrator rights.'
        }

    def checksum(msg):
        sum = 0
        size = (len(msg) // 2) * 2
        for c in range(0,size, 2):
            sum = (sum + ord(msg[c + 1])*256+ord(msg[c])) & 0xffffffff
        if size < len(msg):
            sum = (sum+ord(msg[len(msg) - 1])) & 0xffffffff
        ra = ~((sum >> 16) + (sum & 0xffff) + (sum >> 16)) & 0xffff
        ra = ra >> 8 | (ra << 8 & 0xff00)
        return ra

    def mk_packet(size):
        """Make a new echo request packet according to size"""
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, size, 1)
        #data = struct.calcsize('bbHHh') * 'Q'
        data = size * 'Q'
        my_checksum = checksum(CONVERT(header).Str() + data)
        header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,
                             socket.htons(my_checksum), size, 1)
        return header + CONVERT(data).Bytes()

    def receive(my_socket, ssize, stime, timeout):
        while True:
            if timeout <= 0:
                return
            ready = select.select([my_socket], [], [], timeout)
            if ready[0] == []: # Timeout
                return
            received_time = time.time()
            packet, addr = my_socket.recvfrom(1024)
            type, code, checksum, gsize, seq = struct.unpack('bbHHh', packet[20:28]) # Get Header
            if gsize == ssize:
                return received_time - stime
            timeout -= received_time - stime

    def pinging(ip,timeout=1,size=64):
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
        except socket.error as e:
            if e.errno in ERROR_DESCR:
                raise socket.error(''.join((e.args[1], ERROR_DESCR[e.errno])))
            raise
        if size in ['rnd','random']:
            # Maximum size for an unsigned short int c object(65535)
            size = int((id(timeout) * random.random()) % 65535)
        packet = mk_packet(size)
        while packet:
            sent = my_socket.sendto(packet, (ip, 1)) # ICMP have no port, So just put dummy port 1
            packet = packet[sent:]
        delay = receive(my_socket, size, TIME().Time(), timeout)
        my_socket.close()
        if delay:
            return delay,size

    def do_ping(ip,timeout=1,size=64,count=None,interval=0.7,log_format='ping',cancel_func=None):
        ok=1
        i=1
        while True:
            if IS(cancel_func).Cancel():
                return -1,'canceled'
            delay=pinging(ip,timeout,size)
            if delay:
                ok=0
                if log_format == '.':
                    sys.stdout.write('.')
                    sys.stdout.flush()
                elif log_format == 'ping':
                    sys.stdout.write('{} bytes from {}: icmp_seq={} ttl={} time={} ms\n'.format(delay[1],ip,i,size,round(delay[0]*1000.0,4)))
                    sys.stdout.flush()
            else:
                ok=1
                if log_format == '.':
                    sys.stdout.write('x')
                    sys.stdout.flush()
                elif log_format == 'ping':
                    sys.stdout.write('{} icmp_seq={} timeout ({} second)\n'.format(ip,i,timeout))
                    sys.stdout.flush()
            if count:
                count-=1
                if count < 1:
                    return ok,'{} is alive'.format(ip)
            i+=1
            TIME().Sleep(interval)


    if log_format=='ping':
        if IS('ping').Bin():
            os.system("ping -c {0} {1}".format(count,host))
        else:
            do_ping(host,timeout=timeout,size=64,count=count,log_format='ping',cancel_func=cancel_func)
    else:
        Time=TIME()
        init_sec=Time.Init()
        chk_sec=Time.Init()
        log_type=type(log).__name__
        found_lost=False
        if keep_good > 0 or not count:
           try:
               timeout=int(timeout)
           except:
               timeout=1
           if timeout < keep_good:
               count=keep_good+(2*interval)
               timeout=keep_good+5
           elif not count:
               count=timeout//interval + 3
           elif count * interval > timeout:
               timeout=count*interval+timeout
        good=False
        while count > 0:
           if IS(cancel_func).Cancel():
               log(' - Canceled ping')
               return False
           if stop_func:
               if log_type == 'function':
                   log(' - Stopped ping')
               return False
           if IS('ping').Bin():
               rc=SHELL().Run("ping -c 1 {}".format(host))
           else:
               rc=do_ping(host,timeout=1,size=64,count=1,log_format=None)
           if rc[0] == 0:
              good=True
              if keep_good:
                  if good and keep_good and TIME().Now(int) - chk_sec >= keep_good:
                      return True
              else:
                  return True
              if log_type == 'function':
                  log('.',direct=True,log_level=1)
           else:
              good=False
              chk_sec=TIME().Now(int)
              if log_type == 'function':
                  log('x',direct=True,log_level=1)
           if TIME().Now(int) - init_sec > timeout:
               return False
           TIME().Sleep(interval)
           count-=1
        return good
