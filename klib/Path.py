#Kage Park

def Path(*inp,**opts):
    sym=opts.get('sym','/')
    default=opts.get('default','')
    out=opts.get('out','str')
    if inp:
        full_path=[]
        if isinstance(inp[0],str):
            for zz in inp[0].split(sym):
                if full_path and not zz: continue
                full_path.append(zz)
        for ii in inp[1:]:
            if isinstance(ii,str):
                for zz in ii.split(sym):
                    if full_path and not zz: continue
                    if zz == '.': continue
                    if full_path and full_path[-1] != '..' and zz == '..':
                        del full_path[-1]
                        continue
                    full_path.append(zz)
        if full_path:
            if out in [str,'str']:return sym.join(full_path)
            return full_path
    return default

