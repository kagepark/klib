#Kage Park
from klib.CONVERT import CONVERT
from distutils.spawn import find_executable

class FILE:
    def __init__(self,src):
        self.src=src

    def Rw(self,name,data=None,out='string',append=False,read=None,overwrite=True):
        if isinstance(name,str):
            if data is None:
                if os.path.isfile(name):
                    try:
                        if read in ['firstread','firstline','first_line','head','readline']:
                            with open(name,'rb') as f:
                                data=f.readline()
                        else:
                            with open(name,'rb') as f:
                                data=f.read()
                    except:
                        pass
                    if data is not None:
                        if out in ['string','str']:
                            return True,CONVERT(data).Str()
                        else:
                            return True,data
                return False,'File({}) not found'.format(name)
            else:
                file_path=os.path.dirname(name)
                if not file_path or os.path.isdir(file_path): # current dir or correct directory
                    try:
                        if append:
                            with open(name,'ab') as f:
                                f.write(CONVERT(data).Bytes())
                        else:
                            with open(name,'wb') as f:
                                f.write(CONVERT(data).Bytes())
                        return True,None
                    except:
                        pass
                return False,'Directory({}) not found'.format(file_path)
        return False,'Unknown type({}) filename'.format(name)


    def Mode(self,val):
        if isinstance(val,int):
            if val > 511:
                return oct(val)[-4:]
            elif val > 63:
                return oct(val)
        elif isinstance(val,str):
            cnt=len(val)
            num=int(val)
            if cnt >=3 and cnt <=4 and num >= 100 and num <= 777:
                return int(val,8)

    def Get(self,filename,**opts):
        md5sum=opts.get('md5sum',False)
        data=opts.get('data',False)
        include_dir=opts.get('include_dir',False)
        include_sub_dir=opts.get('include_sub_dir',False)

        def get_file_data(self,filename,root_path=None):
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
        if type(filename) is str:
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

