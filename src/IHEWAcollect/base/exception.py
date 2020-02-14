# -*- coding: utf-8 -*-
"""
**Exception**

https://julien.danjou.info/python-exceptions-guide/
"""
import os

# General modules


class IHEClassInitError(Exception):
    """IHEClassInitError Class

    Args:
        mod (str): Module name.
        msg (bool): Extra message.
    """
    def __init__(self, mod, msg=None):
        if msg is None:
            self.msg = 'Class "{m}" init error.'.format(
                m=mod)

    def __str__(self):
        # __str__() obviously expects a string to be returned,
        # so make sure not to send any other data types
        return repr(self.msg)


class IHEFileError(Exception):
    """IHEFileError Class

    Args:
        file (str): File name.
        msg (bool): Extra message.
    """
    def __init__(self, file, msg=None):
        fpath, fname = os.path.split(file)
        if msg is None:
            self.msg = '"{f}" not found in "{p}".'.format(
                f=fname,
                p=fpath)
        self.file = fname
        self.path = fpath

    def __str__(self):
        # __str__() obviously expects a string to be returned,
        # so make sure not to send any other data types
        return repr(self.msg)


class IHEKeyError(Exception):
    """IHEKeyError Class

    Args:
        key (str): Key name.
        val (list): Key name list.
        msg (bool): Extra message.
    """
    def __init__(self, key, val, msg=None):
        if msg is None:
            self.msg = '"{k}" not found in "{v}".'.format(
                k=key,
                v=val)
        self.key = key
        self.val = val

    def __str__(self):
        # __str__() obviously expects a string to be returned,
        # so make sure not to send any other data types
        return repr(self.msg)


class IHETypeError(Exception):
    """IHETypeError Class

    Args:
        vname (str): Variable name.
        rtype (str): Required type.
        vdata (float): Variable value.
        msg (bool): Extra message.
    """
    def __init__(self, vname, rtype, vdata, msg=None):
        if msg is None:
            self.msg = '"{n}" requires {t}, received "{d}".'.format(
                n=vname,
                t=rtype,
                d=type(vdata))
        self.vname = vname
        self.rtype = rtype
        self.vdata = vdata

    def __str__(self):
        # __str__() obviously expects a string to be returned,
        # so make sure not to send any other data types
        return repr(self.msg)


class IHEStringError(Exception):
    """IHEStringError Class

    Args:
        vname (str): Variable name.
        msg (bool): Extra message.
    """
    def __init__(self, vname, msg=None):
        if msg is None:
            self.msg = '"{k}" received empty string.'.format(
                k=vname)
        self.name = vname

    def __str__(self):
        # __str__() obviously expects a string to be returned,
        # so make sure not to send any other data types
        return repr(self.msg)
