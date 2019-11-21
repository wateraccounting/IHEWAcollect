# -*- coding: utf-8 -*-
"""
**Accounts**

`Restrictions`

The data and this python file may not be distributed to others without
permission of the WA+ team.

`Description`

Before use this module, set account information
in the ``IHEWAcollect/accounts.yml`` file.

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
    from .base import Base
except ImportError:
    from src.IHEWAcollect.base.base import Base


class Accounts(Base):
    """This Accounts class

    Description

    Args:
      workspace (str): Directory to accounts.yml.
      account (str): Account name of data product.
      is_status (bool): Is to print status message.
      kwargs (dict): Other arguments.
    """
    __conf = {
        'path': '',
        'file': 'accounts.yml-encrypted',
        'account': {},
        'data': {
            'credential': {
                'file': 'credential.yml',
                'password': 'W@t3r@ccounting',
                'length': 32,
                'iterations': 100000,
                'salt': 'WaterAccounting_',
                'key': b'OzdmSGV76EmKWVS-MzhWMAa3B4c_oFdbuX8_iSDqbZo='
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

    def __init__(self, workspace, account, is_status, **kwargs):
        """Class instantiation
        """
        Base.__init__(self, is_status)
        # super(Accounts, self).__init__(is_status)

        self.stmsg = {
            0: 'S: WA.Accounts "{f}" status {c}: {m}',
            1: 'E: WA.Accounts "{f}" status {c}: {m}',
            2: 'W: WA.Accounts "{f}" status {c}: {m}',
        }
        self.stcode = 0
        self.status = 'Accounts status.'

        for argkey, argval in kwargs.items():
            if argkey == 'passward':
                self.__conf['data']['credential'][argkey] = argval
            if argkey == 'key':
                self.__conf['data']['credential'][argkey] = argval

        if isinstance(workspace, str):
            if workspace != '':
                self.__conf['path'] = workspace
            else:
                self.__conf['path'] = os.path.join(
                    self._Base__conf['path'], '../', '../', '../'
                )
            if self.is_status:
                print('I: "{k:10}": "{v}"'
                      .format(k='workspace',
                              v=self.__conf['path']))
        else:
            raise TypeError('"{k}" requires string, received "{t}"'
                            .format(k='workspace',
                                    t=type(workspace)))

        if isinstance(account, str):
            if account != '':
                self.__conf['account'][account] = {}
            else:
                self.__conf['account']['FTP_WA_GUESS'] = {}
            if self.is_status:
                print('I: "{k:10}": "{v}"'
                      .format(k='account',
                              v=self.__conf['account']))
        else:
            raise TypeError('"{k}" requires string, received "{t}"'
                            .format(k='account',
                                    t=type(account)))

        if self.stcode == 0:
            self._user()
            message = '"{f}" key is: "{v}"'.format(
                f=self.__conf['file'],
                v=self.__conf['data']['credential']['key'])

        self._status(
            inspect.currentframe().f_code.co_name,
            prt=self.is_status,
            ext=message)

    def _status(self, fun, prt=False, ext=''):
        """Set status

        Args:
          fun (str): Function name.
          prt (bool): Is to print on screen?
          ext (str): Extra message.
        """
        self.status = self.set_status(self.stcode, fun, prt, ext)

    def _user(self):
        """Get user information

        This is the main function to configure user's credentials.

        **Don't synchronize the details to github.**

        - File to read: ``accounts.yml-encrypted``
        - File to read: ``credential.yml``
        """
        f_cfg_org = os.path.join(self.__conf['path'],
                                 self.__conf['file'].split('-encrypted')[0])
        f_cfg_enc = os.path.join(self.__conf['path'],
                                 self.__conf['file'])
        f_crd = os.path.join(self.__conf['path'],
                             self.__conf['data']['credential']['file'])

        if not os.path.exists(f_cfg_enc):
            raise FileNotFoundError('User "{f}" not found.'.format(f=f_cfg_enc))
        if not os.path.exists(f_crd):
            raise FileNotFoundError('User "{f}" not found.'.format(f=f_crd))

        self._user_key(f_crd)
        # self._user_encrypt(f_cfg_org)

        conf = yaml.load(
            self._user_decrypt(f_cfg_enc),
            Loader=yaml.FullLoader)

        for key in conf:
            # __conf.data[accounts, ]
            try:
                self.__conf['data'][key] = conf[key]
                self.stcode = 0
            except KeyError:
                raise KeyError('Key "{k}" not found in "{f}".'
                               .format(k=key, f=f_cfg_enc))
            else:
                # __conf.account
                for subkey in self.__conf['account']:
                    try:
                        self.__conf['account'][subkey] = conf[key][subkey]
                        self.stcode = 0
                    except KeyError:
                        raise KeyError('Sub key "{k}" not found in "{f}".'
                                       .format(k=subkey, f=f_cfg_enc))

        self._status(
            inspect.currentframe().f_code.co_name,
            prt=self.is_status,
            ext='')

    def _user_key(self, file):
        """Getting a key

        This function fun.

        Returns:
          bytes: A URL-safe base64-encoded 32-byte key.
          This must be kept secret.
          Anyone with this key is able to create and read messages.
        """
        f_in = file
        key = b''

        with open(f_in, 'rb') as fp_in:
            key = fp_in.read()

            self.__conf['data']['credential']['key'] = key

        return key

    def _user_key_generator(self):
        """Getting a key

        This function fun.

        Returns:
          bytes: A URL-safe base64-encoded 32-byte key.
          This must be kept secret.
          Anyone with this key is able to create and read messages.
        """
        # from cryptography.fernet import Fernet
        # key = Fernet.generate_key()

        # Convert to type bytes
        pswd = self.__conf['data']['credential']['password'].encode()
        salt = self.__conf['data']['credential']['salt'].encode()
        length = self.__conf['data']['credential']['length']
        iterations = self.__conf['data']['credential']['iterations']

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            salt=salt,
            length=length,
            iterations=iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(pswd))

        return key

    def _user_encrypt(self, file):
        """Encrypt file with given key

        This function encrypt accounts.yml file.

        Args:
          file (str): File name.

        Returns:
          bytes: A URL-safe base64-encoded 32-byte key.
          This must be kept secret.
          Anyone with this key is able to create and read messages.
        """
        f_in = file
        f_out = '{f}-encrypted'.format(f=f_in)
        key = self.__conf['data']['credential']['key']

        with open(f_in, 'rb') as fp_in:
            data = fp_in.read()

        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        with open(f_out, 'wb') as fp_out:
            fp_out.write(encrypted)

        return key

    def _user_decrypt(self, file):
        """Decrypt file with given key

        This function decrypt accounts.yml file.

        Args:
          file (str): File name.

        Returns:
          str: Decrypted Yaml data by utf-8.
        """
        f_in = file
        decrypted = ''

        key = self.__conf['data']['credential']['key']

        with open(f_in, 'rb') as fp_in:
            data = fp_in.read()

            decrypted = Fernet(key).decrypt(data).decode('utf8')

        return decrypted

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
        if key in self.__conf:
            self.stcode = 0
        else:
            self.stcode = 1
            raise KeyError('Key "{k}" not found in "{v}".'
                           .format(k=key, v=self.__conf.keys()))

        self._status(
            inspect.currentframe().f_code.co_name,
            prt=self.is_status,
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
    accounts = Accounts('', 'FTP_WA', is_status=True)

    # Base attributes
    print('\naccounts._Base__conf\n=====')
    pprint(accounts._Base__conf)

    # Accounts attributes
    print('\naccounts._Accounts__conf\n=====')
    pprint(accounts._Accounts__conf)

    # Accounts methods
    print('\naccounts.Base.get_status()\n=====')
    pprint(accounts.get_status())


if __name__ == "__main__":
    main()
