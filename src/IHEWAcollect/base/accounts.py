# -*- coding: utf-8 -*-
"""
**Accounts**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Before use this module, set account information
in the ``accounts.yml`` file.

**Examples:**
::

    import os
    from IHEWAcollect.base.accounts import Accounts
    accounts = Accounts(os.getcwd(), 'FTP_WA_GUESS', is_status=True)

.. note::

    1. Create ``accounts.yml`` under root folder of the project,
       based on the ``config-example.yml``.
    #. Run ``Accounts.credential.encrypt_cfg(path, file, password)``
       to generate ``accounts.yml-encrypted`` file.
    #. Save key to ``credential.yml``.

"""
import os
import sys
import inspect
# import shutil
import yaml
# from datetime import datetime

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from .exception import \
        IHEStringError, IHETypeError, IHEKeyError, IHEFileError
except ImportError:
    from src.IHEWAcollect.base.exception \
        import IHEStringError, IHETypeError, IHEKeyError, IHEFileError

try:
    from .base import Base
except ImportError:
    from src.IHEWAcollect.base.base import Base


class Accounts(Base):
    """This Accounts class

    Description

    Args:
      workspace (str): Directory to accounts.yml.
      product (str): Product name of data products.
      is_status (bool): Is to print status message.
      kwargs (dict): Other arguments.
    """
    status = 'Global status.'

    __status = {
        'messages': {
            0: 'S: WA.Accounts {f:>20} : status {c}, {m}',
            1: 'E: WA.Accounts {f:>20} : status {c}: {m}',
            2: 'W: WA.Accounts {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'path': os.path.join(
            os.getcwd(),
            os.path.dirname(
                inspect.getfile(
                    inspect.currentframe())),
            '../', '../', '../'),
        'file': 'accounts.yml-encrypted',
        'product': {},
        'account': {},
        'data': {
            'credential': {
                'file': 'accounts.yml-credential',
                'password': b'',
                'length': 32,
                'iterations': 100000,
                'salt': b'WaterAccounting_',
                'key': b''
            },
            'accounts': {
                'NASA': {},
                'GLEAM': {},
                'FTP_WA': {},
                'FTP_WA_GUESS': {},
                'MSWEP': {},
                'Copernicus': {},
                'VITO': {}
            },
        }
    }

    def __init__(self, workspace, product, is_status, **kwargs):
        """Class instantiation
        """
        Base.__init__(self, is_status)
        # super(Accounts, self).__init__(is_status)

        for argkey, argval in kwargs.items():
            if argkey == 'others':
                self.argkey = argval

        vname, rtype, vdata = 'is_status', bool, is_status
        if self.check_input(vname, rtype, vdata):
            self.__status['is_print'] = vdata
        else:
            self.__status['code'] = 1

        vname, rtype, vdata = 'workspace', str, workspace
        if self.check_input(vname, rtype, vdata):
            self.__conf['path'] = vdata
        else:
            self.__status['code'] = 1

        vname, rtype, vdata = 'product', str, product
        if self.check_input(vname, rtype, vdata):
            if vdata not in self._Base__conf['data']['products'].keys():
                self.__status['code'] = 1
                raise IHEKeyError(vdata,
                                  self._Base__conf['data']['products'].keys()) from None
            else:
                account = self._Base__conf['data']['products'][vdata]['account']
                self.__conf['account'][account] = {}
                self.__conf['product'] = self._Base__conf['data']['products'][vdata]
        else:
            self.__status['code'] = 1

        if self.__status['code'] == 0:
            self._user()
            self.__status['message'] = '"{f}" key is: "{v}"'.format(
                f=self.__conf['file'],
                v=self.__conf['data']['credential']['key'])

    def _user(self):
        """Get user information

        This is the main function to configure user's credentials.

        **Don't synchronize the details to github.**

        - File to read: ``accounts.yml-encrypted``
        - File to read: ``credential.yml``
        """
        conf_enc = None
        fname_org = 'accounts.yml'
        fname_enc = 'accounts.yml-encrypted'
        fname_crd = 'accounts.yml-credential'
        f_cfg_org = os.path.join(self.__conf['path'], fname_org)
        f_cfg_enc = os.path.join(self.__conf['path'], fname_enc)
        f_cfg_crd = os.path.join(self.__conf['path'], fname_crd)

        if os.path.exists(f_cfg_crd):
            is_enc = self._user_key(f_cfg_crd)
            if is_enc:
                self._user_encrypt(f_cfg_org)
        else:
            self.__status['code'] = 1
            raise IHEFileError(f_cfg_crd) from None

        if os.path.exists(f_cfg_enc):
            conf_enc = yaml.load(self._user_decrypt(f_cfg_enc), Loader=yaml.FullLoader)
            for key in conf_enc:
                try:
                    self.__conf['data'][key] = conf_enc[key]
                except KeyError:
                    self.__status['code'] = 1
                    raise IHEKeyError(key, fname_enc) from None
                else:
                    for subkey in self.__conf['account']:
                        try:
                            self.__conf['account'][subkey] = conf_enc[key][subkey]
                        except KeyError:
                            raise IHEKeyError(subkey, fname_enc) from None
                        else:
                            self.__status['code'] = 0
        else:
            self.__status['code'] = 1
            raise IHEFileError(f_cfg_enc) from None

        self.set_status(
            inspect.currentframe().f_code.co_name,
            prt=self.__status['is_print'],
            ext='')

    def _user_key(self, file) -> bytes:
        """Getting a key

        This function fun.

        A URL-safe base64-encoded 32-byte key.
        This must be kept secret.
        Anyone with this key is able to create and read messages.

        Args:
          file (str): File name.
        """
        is_renew = False
        conf = yaml.load(open(file, 'r'), Loader=yaml.FullLoader)

        if conf is None:
            print('W: {f} is empty.'.format(f=file))
            pswd = input('\33[91m'
                         'IHEWAcollect: Enter your password: '
                         '\33[0m')
            pswd = pswd.strip()
            if pswd != '':
                is_renew = True
                conf = {
                    'password': pswd,
                }
            else:
                raise IHEKeyError('password', conf.keys()) from None

        # password, Yaml load/Python input
        try:
            pswd = conf['password']
        except KeyError:
            pswd = input('\33[91m'
                         'IHEWAcollect: Enter your password: '
                         '\33[0m')
            pswd = pswd.strip()
            if pswd != '':
                # is_renew = True
                pass
            else:
                raise IHEStringError('password') from None
        finally:
            self.__conf['data']['credential']['password'] = str.encode(pswd)

        # key, Yaml load/Python input/Python generate
        try:
            key = conf['key']
        except KeyError:
            print('W: "{k}"'
                  ' not found in "{f}".'
                  .format(k='key', f=conf))

            is_key = input('\33[91m'
                           'IHEWAcollect: Generate your key (y/n): '
                           '\33[0m')
            if is_key in ['Y', 'YES', 'y', 'Yes']:
                key = self._user_key_generator()
                is_renew = True
            else:
                raise IHEKeyError('key', conf.keys()) from None
        finally:
            self.__conf['data']['credential']['key'] = str.encode(key)

        # Final check
        key_from_pswd = str.encode(self._user_key_generator())
        key_from_conf = self.__conf['data']['credential']['key']
        if key_from_pswd == key_from_conf:
            return is_renew
        else:
            raise Exception('E: "password" not match "key".')

    def _user_key_generator(self) -> str:
        """Getting a key

        This function fun.

        A URL-safe base64-encoded 32-byte key.
        This must be kept secret.
        Anyone with this key is able to create and read messages.

        Args:
          file (str): File name.
          pswd (bytes): Password.

        Returns:
          str: key
        """
        # from cryptography.fernet import Fernet
        # key = Fernet.generate_key()

        length = self.__conf['data']['credential']['length']
        iterations = self.__conf['data']['credential']['iterations']
        salt = self.__conf['data']['credential']['salt']
        pswd = self.__conf['data']['credential']['password']

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            salt=salt,
            length=length,
            iterations=iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(pswd))

        return key.decode()

    def _user_encrypt(self, file):
        """Encrypt file with given key

        This function encrypt accounts.yml file.

        Args:
          file (str): Encrypted file name.
        """
        pswd = self.__conf['data']['credential']['password']
        key = self.__conf['data']['credential']['key']

        file_org = file
        file_enc = file_org + '-encrypted'
        file_crd = file_org + '-credential'

        if os.path.exists(file_org):
            with open(file_org, 'rb') as fp_in:
                data = fp_in.read()

            with open(file_enc, 'wb') as fp_out:
                fernet = Fernet(key)
                encrypted = fernet.encrypt(data)
                fp_out.write(encrypted)

            with open(file_crd, 'w') as fp_out:
                fp_out.write('# password should be deleted!\n')
                fp_out.write('# password: "{}"\n'.format(pswd.decode()))
                fp_out.write('key: "{}"\n'.format(key.decode()))
        else:
            raise IHEFileError(file_org) from None

    def _user_decrypt(self, file) -> str:
        """Decrypt file with given key

        This function decrypt accounts.yml file.

        Args:
          file (str): File name.

        Returns:
          str: Decrypted Yaml data by utf-8.
        """
        key = self.__conf['data']['credential']['key']

        if os.path.exists(file):
            with open(file, 'rb') as fp_in:
                data = fp_in.read()

                decrypted = Fernet(key).decrypt(data).decode('utf8')

                return decrypted
        else:
            raise FileNotFoundError('IHEWAcollect: "{f}"'
                                    ' not found.'.format(f=file))

    def set_status(self, fun='', prt=False, ext=''):
        """Set status

        Args:
          fun (str): Function name.
          prt (bool): Is to print on screen?
          ext (str): Extra message.
        """
        self.status = self._status(self.__status['messages'],
                                   self.__status['code'],
                                   fun, prt, ext)

    def get_user(self, key):
        """Get user information

        This is the function to get user's configuration data.

        **Don't synchronize the details to github.**

        - File to read: ``credential.yml``
          contains key: ``accounts.yml-encrypted``.
        - File to read: ``accounts.yml-encrypted``
          generated from: ``accounts.yml``.

        Args:
          key (str): Key name.

        Returns:
          dict: User data.

        :Example:

            >>> import os
            >>> from IHEWAcollect.base.accounts import Accounts
            >>> accounts = Accounts(os.getcwd(), 'FTP_WA_GUESS', is_status=False)
            >>> account = accounts.get_user('account')
            >>> account['FTP_WA_GUESS']
            {'username': 'wateraccountingguest', 'password': 'W@t3r@ccounting', ...
            >>> accounts = accounts.get_user('accounts')
            Traceback (most recent call last):
            ...
            KeyError:
        """
        fun_name =inspect.currentframe().f_code.co_name
        if key in self.__conf:
            self.__stcode = 0
        else:
            self.__stcode = 1
            raise KeyError('Key "{k}" not found in "{v}".'
                           .format(k=key, v=self.__conf.keys()))

        self.set_status(
            fun=fun_name,
            prt=self.__prtstd,
            ext='')
        return self.__conf[key]

    @staticmethod
    def wait_bar(i, total,
                 prefix='', suffix='',
                 decimals=1, length=100, fill='█'):
        """Wait Bar Console

        This function will print a waitbar in the console

        Args:
          i (int): Iteration number.
          total (int): Total iterations.
          prefix (str): Prefix name of bar.
          suffix (str): Suffix name of bar.
          decimals (int): Decimal of the wait bar.
          length (int): Width of the wait bar.
          fill (str): Bar fill.
        """
        # Adjust when it is a linux computer
        if os.name == 'posix' and total == 0:
            total = 0.0001

        percent = ('{0:.' + str(decimals) + 'f}').format(100 *
                                                         (i / float(total)))
        filled = int(length * i // total)
        bar = fill * filled + '-' * (length - filled)

        sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
        sys.stdout.flush()

        if i == total:
            print()


def main():
    from pprint import pprint

    # @classmethod
    # print('\nAccounts.check_conf()\n=====')
    # pprint(Accounts.check_conf('data', is_status=False))

    # Accounts __init__
    print('\nAccounts\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())),
        '../', '../', '../'
    )
    accounts = Accounts(path, 'ALEXI', is_status=True)

    # Base attributes
    print('\naccounts._Base__conf\n=====')
    # pprint(accounts._Base__conf)

    # Accounts attributes
    print('\naccounts._Accounts__conf\n=====')
    print(accounts._Accounts__conf['data']['accounts'].keys())
    # pprint(accounts._Accounts__conf)

    # Accounts methods
    print('\naccounts.get_status()\n=====')
    pprint(accounts.get_status())


if __name__ == "__main__":
    main()
