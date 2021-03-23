class L(list):
    def __new__(cls, inp=None):
        if inp:return list(inp)
        return []

l=L([1,2,3])
print(l,type(l))
l.append(1)
print(l,type(l))
