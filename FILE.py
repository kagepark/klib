#Kage Park
from distutils.spawn import find_executable
import os
import fnmatch
from klib.MODULE import *
MODULE().Import('from klib.CONVERT import CONVERT')
MODULE().Import('import magic')
MODULE().Import('import tarfile')
MODULE().Import('import zipfile')

class FILE:
    def __init__(self,src):
        self.src=src

    def Info(self,filename=None,default={},data=False):
        if filename is None:
            filename=self.src
        rt={}
        if isinstance(filename,str) and os.path.isfile(filename):
            rt['path']=os.path.dirname(filename)
            filename_info=os.path.basename(filename).split('.')
            rt['filename']=filename_info
            if 'tar' in filename_info:
                idx=filename_info.index('tar')
            else:
                idx=-1
            rt['name']='.'.join(filename_info[:idx])
            rt['ext']='.'.join(filename_info[idx:])
            aa=magic.from_buffer(open(filename,'rb').read(2048))
            if aa:
                rt['type']=aa.split()[0].lower()
            else:
                rt['type']='unknown'
            state=os.stat(filename)
            rt['size']=state.st_size
            rt['mode']=state.st_mode
            rt['atime']=state.st_atime
            rt['mtime']=state.st_mtime
            rt['ctime']=state.st_ctime
            rt['gid']=state.st_gid
            rt['uid']=state.st_uid
            rt['link']=state.st_nlink
            if data:
                filedata=self.Rw(filename)
                if filedata[0]:
                    rt['data']=filedata[1]
        return rt

    def ExecFile(self,filename=None,bin_name=None,default=None,work_path='/tmp'):
        # check the filename is excutable in the system bin file then return the file name
        # if compressed file then extract the file and find bin_name file in the extracted directory
        #   and found binary file then return then binary file path
        # if filename is excutable file then return the file path
        # if not found then return default value
        if filename is None: filename=self.src
        info=self.Info(filename)
        if info:
            if info['type'] in ['elf'] and info['mode'] == 33261:return self.src
            if self.Extract(work_path=work_path,info=info):
                if bin_name:
                    rt=[]
                    for ff in self.Find(work_path,filename=bin_name):
                        if self.Info(ff).get('mode') == 33261:
                            rt.append(ff)
                    return rt
        else:
            if find_executable(self.src): return self.src
        return default

    def Basename(self,filename=None,default=False):
        if filename is None: filename=self.src
        if isinstance(filename,str):return os.path.basename(filename)
        return default
        
    def Dirname(self,filename=None,bin_name=None,default=False):
        if filename is None: filename=self.src
        if not isinstance(filename,str): return default
        if bin_name is None: return os.path.dirname(filename)
        if not isinstance(bin_name,str): return default
        bin_info=bin_name.split('/')
        bin_n=len(bin_info)
        filename_info=filename.split('/')
        filename_n=len(filename_info)
        for ii in range(0,bin_n):
            if filename_info[filename_n-1-ii] != bin_info[bin_n-1-ii]: return default
        return '/'.join(filename_info[:-bin_n])

    def Find(self,root_path,filename=None,default=[]):
        if not isinstance(root_path,str): return default
        if filename is None:
            filename=self.src
        if not isinstance(filename,str): return default
        filename=os.path.basename(filename)
        if os.path.isdir(root_path):
            rt = []
            for base, dirs, files in os.walk(root_path):
                found = fnmatch.filter(files, filename)
                rt.extend(os.path.join(base, f) for f in found)
            return rt
        return default
 
    def Extract(self,work_path='/tmp',info={},del_org_file=False):
        if not info:
            info=self.Info()
        filetype=info.get('type',None)
        fileext=info.get('ext',None)
        if filetype and fileext:
            # Tar stuff
            if fileext in ['tgz','tar','tar.gz','tar.bz2','tar.xz'] and filetype in ['gzip','tar','bzip2','lzma','xz','bz2']:
                tf=tarfile.open(self.src)
                tf.extractall(work_path)
                tf.close()
            elif fileext in ['zip'] and filetype in ['compress']:
                with zipfile.ZipFile(self.src,'r') as zf:
                    zf.extractall(work_path)
            if del_org_file: os.unline(self.src)
            return True
        return False

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

