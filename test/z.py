from functools import wraps

def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator


a=list()

@add_method(a)
def Append(self,inp):
    self.append(inp)

a.append(1)
print(a)
a.Append(2)
print(a)
