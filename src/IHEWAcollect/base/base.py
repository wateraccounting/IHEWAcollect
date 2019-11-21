# -*- coding: utf-8 -*-
"""
**Base**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Before use this module, set account information
in the ``IHEWAcollect/accounts.yml`` file.

**Examples:**
::

    from IHEWAcollect.base.base import Base
    base = Base(is_status=True)

.. todo::

    1. 20191010, QPan, add section **sources** from ``self.__conf`` to ``base.yml``
"""
import os
import sys
import inspect
# import shutil
import yaml
# from datetime import datetime

# try:
#     # setup.py
#     from .base import Base
# except ImportError:
#     # PyCharm
#     from src.IHEWAcollect.base.base import Base
#
# PyCharm
# if __name__ == "__main__":
#
# >>> from .base import Base
# ImportError: cannot import name 'base' from '__main__'
# But works for setup.py
#
# >>> from base import Base
# ModuleNotFoundError
#
# PyCharm->Project Structure->"Sources": WaterAccounting\""
# from src.IHEWAcollect.base.base import Base
# OK
#
# PyCharm->Project Structure->"Sources": IHEWAcollect\"src\IHEWAcollect"
# >>> from base import Base
# OK


class Base(object):
    """This Base class

    Args:
      is_status (bool): Is to print status message.
    """
    __conf = {
        'path': os.path.join(
            os.getcwd(),
            os.path.dirname(
                inspect.getfile(
                    inspect.currentframe()))),
        'file': 'base.yml',
        'data': {
            'messages': {},
            'products': {}
        }
    }

    def __init__(self, is_status):
        """Class instantiation
        """
        self.stmsg = {
            0: 'S: WA.Base "{f}" status {c}: {m}',
            1: 'E: WA.Base "{f}" status {c}: {m}',
            2: 'W: WA.Base "{f}" status {c}: {m}',
        }
        self.stcode = 0
        self.status = 'Base status.'

        if isinstance(is_status, bool):
            self.is_status = is_status
        else:
            raise TypeError('"{k}" requires bool, received "{t}"'
                            .format(k='is_status',
                                    t=type(is_status)))

        self.set_conf()
        self.set_status(
            self.stcode,
            inspect.currentframe().f_code.co_name,
            prt=self.is_status,
            ext='')

    def set_conf(self):
        """Get configuration

        This function open collect.cfg configuration file.
        """
        f_in = os.path.join(self.__conf['path'],
                            self.__conf['file'])

        if not os.path.exists(f_in):
            raise FileNotFoundError('Collect "{f}" not found.'.format(f=f_in))

        conf = yaml.load(open(f_in, 'r'), Loader=yaml.FullLoader)

        for key in conf:
            # __conf.data[messages, ]
            try:
                self.__conf['data'][key] = conf[key]
                self.stcode = 0
            except KeyError:
                raise KeyError(
                    '"{k}" not found in "{f}".'.format(
                        k=key, f=f_in))

        self.set_status(
            self.stcode,
            inspect.currentframe().f_code.co_name,
            prt=self.is_status,
            ext='')

    def set_status(self, cod, fun, prt=False, ext=''):
        """Set Status

        Returns:
          str: Status message.
        """
        # cod = self.stcode
        # msg = self._Base__conf['data']['messages'][cod]['msg']
        # lvl = self._Base__conf['data']['messages'][cod]['level']
        # if ext != '':
        #     self.status = self.stmsg[lvl].format(
        #         f=fun, c=cod, m='{m}\n   {e}'.format(m=msg, e=ext))
        # else:
        #     self.status = self.stmsg[lvl].format(
        #         f=fun, c=cod, m='{m}'.format(m=msg))
        #
        # self._Base__conf['status'] = self.status
        #
        # if prt:
        #     print(self.status)

        msg = self.__conf['data']['messages'][cod]['msg']
        lvl = self.__conf['data']['messages'][cod]['level']
        if ext != '':
            self.status = self.stmsg[lvl].format(
                f=fun, c=cod, m='{m}\nI: {e}'.format(m=msg, e=ext))
        else:
            self.status = self.stmsg[lvl].format(
                f=fun, c=cod, m='{m}'.format(m=msg))

        if prt:
            print(self.status)

        return self.status

    def get_status(self):
        """Get status

        This is the function to get project status.

        Returns:
          str: Status message.
        """
        return self.status

    def get_conf(self, key):
        """Get configuration information

        This is the function to get project's configuration data.

        Args:
          key (str): Key name.

        Returns:
          dict: Configuration data.

        :Example:

            >>> import os
            >>> from IHEWAcollect.base.base import Base
            >>> base = Base(is_status=False)
            >>> file = base.get_conf('file')
            >>> print(file)
            base.yml
        """
        if key in self.__conf:
            self.stcode = 0
        else:
            self.stcode = 1
            raise KeyError('Key "{k}" not found in "{v}".'
                           .format(k=key, v=self.__conf.keys()))

        return self.__conf[key]

    @classmethod
    def check_conf(cls, key, is_status):
        """Check configuration information

        This is the function to get user's configuration data.

        **Don't synchronize the details to github.**

        - File to read: ``collect.yml``.

        Args:
          key (str): Key name.

        Returns:
          dict: Configuration data.

        :Example:

            >>> from IHEWAcollect.base.base import Base
            >>> conf = Base.check_conf('data', is_status=False)
            >>> conf['messages'][0]
            {'msg': 'No error', 'level': 0}
        """
        # this_class = cls(is_status)
        return cls(is_status).get_conf(key)


def main():
    from pprint import pprint

    print('\n__location__\n=====')
    __location__ = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())))
    print(__location__)
    print('0.1', inspect.currentframe())
    print('0.2', inspect.getfile(
        inspect.currentframe()))
    print('1. getcwd:', os.getcwd())
    print('2. dirname: ', os.path.dirname(
        inspect.getfile(inspect.currentframe())))

    print('\n__file__\n=====')
    print(__file__)

    print('\nBase: sys.path\n=====')
    pprint(sys.path)

    # # @classmethod

    # Base __init__
    print('\nBase\n=====')
    base = Base(is_status=True)

    # Base attributes
    pprint(base._Base__conf)

    # # Base methods


if __name__ == "__main__":
    main()
