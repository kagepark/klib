#Kage Park
class PRINT:
    def __init__(self,*msg,**opts):
        self.color_db=opts.get('color_db',{'blue': 34, 'grey': 30, 'yellow': 33, 'green': 32, 'cyan': 36, 'magenta': 35, 'white': 37, 'red': 31})
        self.bg_color_db=opts.get('bg_color_db',{'cyan': 46, 'white': 47, 'grey': 40, 'yellow': 43, 'blue': 44, 'magenta': 45, 'red': 41, 'green': 42})
        self.attr_db=opts.get('attr_db',{'reverse': 7, 'blink': 5,'concealed': 8, 'underline': 4, 'bold': 1})


        log_p=False
        log=opts.get('log',None)
        log_level=opts.get('log_level',8)
        dsp=opts.get('dsp','a')
        func_name=opts.get('func_name',None)
        date=opts.get('date',False)
        date_format=opts.get('date_format','[%m/%d/%Y %H:%M:%S]')
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
            call_name=GET().ParentName(detail=caller_detail)
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
                 if args and len(args) <= 4 and ('direct' in args or 'log_level' in args or 'func_name' in args):
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
                     if 'func_name' in args:
                         lidx=args.index('func_name')
                         del tmp[lidx]
                         args[lidx]=func_name
                     if 'date_format' in args:
                         lidx=args.index('date_format')
                         del tmp[lidx]
                         args[lidx]=date_format
                     args[tmp[0]]=msg_str
                     log(*args)
                 elif 'keywards' in log_func_arg:
                     log(msg_str,direct=direct,log_level=log_level,func_name=func_name,date_format=date_format)
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
                 sys.stderr.flush()
             else:
                 sys.stdout.write(msg_str+new_line)
                 sys.stdout.flush()
        # return msg
        if 'r' in dsp:
             return msg_str

