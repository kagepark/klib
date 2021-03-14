#Kage Park
class MAC:
    def __init__(self,src):
        self.src=src

    def IsV4(self):
        symbol=opts.get('symbol',':')
        default=opts.get('default',False)
        if isinstance(self.src,str):
            self.src=self.src.strip()
            # make sure the format
            if 12 <= len(self.src) <= 17:
                for i in [':','-']:
                    self.src=self.src.replace(i,'')
                self.src=symbol.join(self.src[i:i+2] for i in range(0,12,2))
            # Check the normal mac format
            octets = self.src.split(symbol)
            if len(octets) != 6: return False
            for i in octets:
                try:
                   if len(i) != 2 or int(i, 16) > 255:
                       return False
                except:
                   return False
            return True
        return default


