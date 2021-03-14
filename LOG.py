#Kage Park
class LOG:
    def __init__(self,src):
        self.src=src

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
