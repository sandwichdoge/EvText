import ctypes
import platform

global hDll
osname = platform.system()
if osname == "Linux":
    # For Linux, use the following. Change the 6 to whatever it is on your computer.
    hDll = ctypes.CDLL("libc.so.6")
elif osname == "Windows":
    hDll = ctypes.cdll.msvcrt


def str_alloc(str):
    buf = ctypes.create_string_buffer(str)
    return buf

def get_address(var):
    return ctypes.addressof(var)

def get_size(var):
    if var._type_ == ctypes.c_char:
        size = ctypes.sizeof(ctypes.c_char) * len(var)
    return size

def free(var):
    addr = get_address(var)
    size = get_size(var)
    ctypes.memset(addr, 0, size)

def get_string(addr, size = 0):
    return ctypes.string_at(addr, size)


"""
ss = str_alloc("data")
print get_size(ss)
print get_address(ss)
"""