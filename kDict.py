import pprint
import sys

def peeling(v,ignore=[],collect=[],jump=None):
  if isinstance(v,dict):
    v=v.copy()
    if jump is not None:
      if jump in v:
         v=v[jump]
    if isinstance(v,dict):
      rc={}
      for k in v:
        if k not in ignore or k in collect:
          if isinstance(v[k],dict) and jump is not None and jump in v[k]:
            vv=v[k][jump]
          else:
            vv=v[k]
          if isinstance(vv,dict):
            rr=peeling(vv,ignore=ignore,jump=jump)
            rc[k]=rr
          else:
            rc[k]=vv
      return rc
  return v

class kDict(dict):
    MARKER = {}
    _p_='._p'
    _d_='._d'
    _n_=True

    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError('expected dict')

    def __getitem__(self, key):
        try:
            found = dict.__getitem__(self,key)
        except:
            found=kDict.MARKER
        #found=self.get(key,kDict.MARKER)
        if found is kDict.MARKER:
            found = kDict()
            super(kDict, self).__setitem__(key, found)
# Property setting issue
        # If the data is not kDict type data then convert the data to kDict type
        # for example: root.abc.test=[1,2,3] => root.abc.PUT('test',[1,2,3]

        #    new_found=kDict({self._d_:found}) # Remove property. because, can known that is fake data or not in the call function.
#            new_found=kDict({self._d_:found, self._p_:{}})
#            super(kDict, self).__setitem__(key,new_found) # If you want change original data then enable
        #    return new_found # it just reutn fake data for ignore error for GET() when the data is not kDict type data.
        return found

    def __setitem__(self, key, value):
        found=self.get(key,None)
        if self._is_ro(found,key=key):
            return False
        if isinstance(found,dict) and self._p_ in found:
            if isinstance(value, dict) and self._d_ in value:
                found[self._d_]=value[self._d_]
            else:
                found[self._d_]=value
            super(kDict, self).__setitem__(key, found)
        else:
            if isinstance(value, dict) and not isinstance(value, kDict):
                value = kDict(value)
            super(kDict, self).__setitem__(key, value)

    # del dictionary[key]
    def __delitem__(self, key):
        if self._is_ro(self.get(key,None),key=key):
            return False
        super(kDict, self).__delitem__(key) # delete data

    def _is_ro(self,found,key=None):
        if isinstance(found, dict) and self._p_ in found and 'readonly' in found[self._p_] and found[self._p_]['readonly']:
            if self._n_:
                if key:
                    sys.stderr.write('item({}) is readonly\n'.format(key))
                else:
                    sys.stderr.write('item is readonly\n')
                sys.stderr.flush()
            return True
        return False

        
    # dictionary.pop(key)
    def POP(self,key):
        if self._is_ro(self.__getitem__(key),key=key):
            return False
        #found = self.get(key, default=None)
        found = self.GET(key, default=None)
        super(kDict, self).__delitem__(key) # delete data
        return found

    def PROPER(self, key=None, value=None):
        if value is not None and key is not None:
            if self._p_ in self:
                self[self._p_][key]=value
                nvalue=self[self._p_]
                super(kDict, self).__setitem__(self._p_,nvalue)
            else:
                #nvalue={key:value}
                if self._n_:
                    sys.stderr.write('the item have no property. if you need property then change the data to kDict type\n')
                    sys.stderr.flush()
                return False
            super(kDict, self).__setitem__(self._p_,nvalue)
            return True
        elif key is not None:
            if self._p_ in self:
                if key in self[self._p_]:
                    return self[self._p_][key]
            return None
        else:
            if self._p_ in self:
                return self[self._p_]
            else:
                return None


    def GET(self,key=None,default=None,raw=False):
        try:
            if key is None:
                if raw:
                    return peeling(self)
                return peeling(self,ignore=[self._p_],jump=self._d_)
            else:
                found=dict.__getitem__(self,key)
                if isinstance(found,dict):
                    if raw:
                        return peeling(found)
                    return peeling(found,ignore=[self._p_],jump=self._d_)
                return found
        except:
            return default

    def CHECK(self,value,idx=0):
        try:
            found=peeling(self,ignore=[self._p_],jump=self._d_)
            type_found=type(found)
            if type_found in [list,tuple]:
                if idx in [None,False,'all','any','*']:
                    if value in found:
                        return True
                else:
                    if value == found[idx]:
                        return True
            elif type_found in [dict]:
                if value in found:
                    return True
            else:
                if value == found:
                    return True
        except:
            pass
        return False

    def PUT(self,key,value,proper={}):
        if value is None:
            return
        if self._is_ro(self.__getitem__(key),key=key):
            return False
        if proper is {}:
            self.__setitem__(key, value)
        else:
            self.__setitem__(key, {self._d_:value,self._p_:proper})
        return value

    def UPDATE(self,data):
        if self._is_ro(self):
            return False
        if isinstance(self,dict) and self._d_ in self:
            self[self._d_].update(data)
        else:
            super(kDict, self).update(data)

    def DEL(self,key):
        if self._is_ro(self.__getitem__(key),key=key):
            return False
        super(kDict, self).__delitem__(key) # delete data

    def CD(self,path):
        path_a=path.split('/')
        for p in path_a:
            if p in self:
                self=self[p]
            else:
                return False
        return self

    def DIFF(self,oo,proper=False):
        if proper:
            diff1=self.copy()
            diff2=oo.copy()
        else:
            diff1=peeling(self.copy(),ignore=[self._p_],jump=self._d_)
            diff2=peeling(oo.copy(),ignore=[self._p_],jump=self._d_)
        if diff1 == diff2:
            return True
        else:
            return False

    def KEYS(self):
        if isinstance(self,dict) and self._p_ in self:
            mm=self.keys()
            mm.remove(self._p_)
            return mm
        return self.keys()

    def LIST(self,keys=[]):
        rc=[]
        for ii in keys:
            if ii in self:
                rc.append(peeling(self[ii],ignore=[self._p_],jump=self._d_))
        return rc

    def LEN(self):
        if isinstance(self,dict) and self._p_ in self:
            return len(self)-1
        return len(self)

    def PRINT(self):
        pprint.pprint(self)

    __setattr__, __getattr__ = __setitem__, __getitem__
