#Kage Park
import syslog
from klib.GET import GET

class LOG:
    def __init__(self,src,log_limit=3,log_file=None,log_file_mode='a+'):
        self.src=src
        self.log_limit=log_limit
        self.log_file=log_file
        self.log_file_mode=log_file_mode

    def Format(self,*msg,**opts):
        log_date_format=opts.get('date_format','[%m/%d/%Y %H:%M:%S]')
        func_name=opts.get('func_name',False)
        log_intro=opts.get('log_intro',3)
        end_new_line=opts.get('end_new_line','')
        start_new_line=opts.get('start_new_line','\n')
        if len(msg) > 0:
            m_str=None
            intro=''
            intro_space=''
            if log_date_format:
                intro=format_time(tformat=log_date_format)+' '
            if func_name or log_intro > 3:
                if type(func_name) is str:
                    intro=intro+'{0} '.format(func_name)
                else:
                    intro=intro+'{0}() '.format(GET().ParentName())
            if intro:
               for i in range(0,len(intro)+1):
                   intro_space=intro_space+' '
            for m in list(msg):
                if m_str is None:
                    m_str='{0}{1}{2}{3}'.format(start_new_line,intro,m,end_new_line)
                else:
                    m_str='{0}{1}{2}{3}{4}'.format(start_new_line,m_str,intro_space,m,end_new_line)
            return m_str

    def Log(self,level,msg,log_type=None,stdout=True,syslogd=False,stdfile=False):
        if sys.log_limit >= level:
            if log_type in ['INFO','info']:
                if syslogd:
                    syslog.syslog(syslog.LOG_INFO,msg)
                if stdout:
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
            elif syslogd in ['KERN','kern']:
                if stdout:
                    sys.stderr.write(msg)
                    sys.stderr.flush()
                if syslogd:
                    syslog.syslog(syslog.LOG_KERN,msg)
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        logfile='{}.ker'.format(logfile)
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
            elif syslogd in ['ERR','err'] or stderr:
                if stdout:
                    sys.stderr.write(msg)
                    sys.stderr.flush()
                if syslogd:
                    syslog.syslog(syslog.LOG_ERR,msg)
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        logfile='{}.err'.format(logfile)
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
            elif syslogd in ['CRIT','crit']:
                if stdout:
                    sys.stderr.write(msg)
                    sys.stderr.flush()
                if syslogd:
                    syslog.syslog(syslog.LOG_CRIT,msg)
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        logfile='{}.cri'.format(logfile)
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
            elif syslogd in ['WARN','warn']:
                if stdout:
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                if syslogd:
                    syslog.syslog(syslog.LOG_WARNING,msg)
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
            elif syslogd in ['DBG','DEBUG','dbg','debug']:
                if syslogd:
                    syslog.syslog(syslog.LOG_DEBUG,msg)
                else:
                    printf(
                if stdout:
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        logfile='{}.dbg'.format(logfile)
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
            else:
                if stdout:
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                if syslogd:
                    syslog.syslog(msg)
                if stdfile and isinstance(self.log_file,(str,tuple,list)):
                    if isinstance(self.log_file,str):
                        self.log_file=self.log_file.split(',') 
                    for logfile in self.log_file:
                        if GET(logfile).Dirname():
                            open with(logfile,self.log_file_mode) as f:
                                f.write(msg)
