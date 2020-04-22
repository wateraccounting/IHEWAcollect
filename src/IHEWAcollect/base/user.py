# -*- coding: utf-8 -*-
"""
**User**

Before use this module, set account information in the ``accounts.yml`` file.

**Examples:**
::

    from IHEWAcollect.base.user import User

    user = User(workspace=path, product='CFSR', is_print=True)

.. note::

    1. Create ``accounts.yml`` under root folder of the project,
       based on the ``config-example.yml``.
    2. Run ``User.credential.encrypt_cfg(path, file, password)``
       to generate ``accounts.yml-encrypted`` file.
    3. Save key to ``credential.yml``.

"""
import base64
import inspect
import os
import sys

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# import shutil
# import datetime



try:
    # IHEClassInitError, IHEStringError, IHETypeError, IHEKeyError, IHEFileError
    from .base.exception import IHEClassInitError,\
        IHEStringError, IHEKeyError, IHEFileError
except ImportError:
    from IHEWAcollect.base.exception import IHEClassInitError,\
        IHEStringError, IHEKeyError, IHEFileError

try:
    from .base import Base
except ImportError:
    from IHEWAcollect.base.base import Base


class User(Base):
    """This User class

    Description

    Args:
        workspace (str): Directory to accounts.yml.
        product (str): Product name of data products.
        is_print (bool): Is to print status message.
        kwargs (dict): Other arguments.
    """
    status = 'Global status.'

    __status = {
        'messages': {
            0: 'S: WA.User     {f:>20} : status {c}, {m}',
            1: 'E: WA.User     {f:>20} : status {c}: {m}',
            2: 'W: WA.User     {f:>20} : status {c}: {m}',
        },
        'code': 0,
        'message': '',
        'is_print': True
    }

    __conf = {
        'credential': {
            'file_crd': 'accounts.yml-credential',
            'file_enc': 'accounts.yml-encrypted',
            'password': b'',
            'length': 32,
            'iterations': 100000,
            'salt': b'WaterAccounting_',
            'key': b''
        },
        'file': 'accounts.yml',
        'path': '',
        'data': {
            'accounts': {},
        },
        'account': {
            'name': '',
            'data': {}
        }
    }

    def __init__(self, workspace, product, is_print, **kwargs):
        """Class instantiation
        """
        # super(User, self).__init__(workspace, product, is_print, **kwargs)
        Base.__init__(self, product, is_print)

        tmp_product = self._Base__conf['product']

        for argkey, argval in kwargs.items():
            if argkey == 'others':
                self.argkey = argval

        # Class self.__status['is_print']
        vname, rtype, vdata = 'is_print', bool, is_print
        if self.check_input(vname, rtype, vdata):
            self.__status['is_print'] = vdata
        else:
            self.__status['code'] = 1

        # Class self.__conf['path']
        vname, rtype, vdata = 'workspace', str, workspace
        if self.check_input(vname, rtype, vdata):
            self.__conf['path'] = vdata
        else:
            self.__status['code'] = 1

        # Class self.__conf['account']['name']
        self.__conf['account']['name'] = tmp_product['data']['account']

        # Class self.__conf['data']
        # Class self.__conf['account']['data']
        if self.__status['code'] == 0:
            self._user()
            self.__status['message'] = 'Key is: "{v}"'.format(
                v=self.__conf['credential']['key'])
        else:
            raise IHEClassInitError('User') from None

    def _user(self):
        """Get user information

        This is the main function to configure user's credentials.

        **Don't synchronize the details to github.**

        - File to read: ``accounts.yml-credential``
        - File to read: ``accounts.yml-encrypted``
        """
        conf_enc = None
        fname_org = self.__conf['file']
        fname_enc = self.__conf['credential']['file_enc']
        fname_crd = self.__conf['credential']['file_crd']
        file_org = os.path.join(self.__conf['path'], fname_org)
        file_enc = os.path.join(self.__conf['path'], fname_enc)
        file_crd = os.path.join(self.__conf['path'], fname_crd)

        if os.path.exists(file_org):
            conf_enc = yaml.load(open(file_org, 'r', encoding='UTF8'),
                                 Loader=yaml.FullLoader)
        else:
            print('"{}" not exist'.format(file_org))
            conf_enc = None

        if conf_enc is None:
            if os.path.exists(file_enc):
                key = self._user_key(file_crd)

                if len(key) > 0:
                    # Load encrypted file
                    conf_enc = yaml.load(self._user_decrypt(file_enc),
                                         Loader=yaml.FullLoader)
                else:
                    # Generate encrypted file
                    conf_enc = self._user_encrypt(file_org)
            else:
                self.__status['code'] = 1
                raise IHEFileError(file_enc) from None

        if isinstance(conf_enc, dict):
            for key in conf_enc:
                try:
                    self.__conf['data'][key] = conf_enc[key]
                except KeyError:
                    self.__status['code'] = 1
                    raise IHEKeyError(key, fname_enc) from None
                else:
                    subkey = self.__conf['account']['name']
                    if subkey is not None:
                        try:
                            self.__conf['account']['data'] = conf_enc[key][subkey]
                        except KeyError:
                            raise IHEKeyError(subkey, fname_enc) from None
                        else:
                            self.__status['code'] = 0
                    else:
                        self.__conf['account']['name'] = ''
                        self.__status['code'] = 0
        else:
            self.__status['code'] = 1

        self.set_status(
            inspect.currentframe().f_code.co_name,
            prt=self.__status['is_print'],
            ext='')

    def _user_key(self, file) -> str:
        """Getting a key

        This function fun.

        A URL-safe base64-encoded 32-byte key.
        This must be kept secret.
        Anyone with this key is able to create and read messages.

        Args:
            file (str): File name.
        """
        pswd = None
        key = None
        conf = None

        if os.path.exists(file):
            conf = yaml.load(open(file, 'r', encoding='UTF8'),
                             Loader=yaml.FullLoader)
        else:
            print('"{}" not exist'.format(file))

        # password, Yaml load/Python input
        if conf is not None and isinstance(conf, dict):
            if 'password' in conf.keys():
                pswd = conf['password']
            else:
                pswd = input('\33[91m'
                             'IHEWAcollect: Enter your password: '
                             '\33[0m')
        else:
            pswd = input('\33[91m'
                         'IHEWAcollect: Enter your password: '
                         '\33[0m')
        pswd = pswd.strip()
        key_from_pswd = self._user_key_generator(pswd)
        # self.__conf['credential']['password'] = str.encode(pswd)

        # key, Yaml load/Python input/Python generate
        if conf is not None and isinstance(conf, dict):
            if 'key' in conf.keys():
                key = conf['key']
            else:
                key = ''
        else:
            key = ''

        # Final check keys
        self.__conf['credential']['password'] = str.encode(pswd)
        if key_from_pswd == key:
            self.__conf['credential']['key'] = str.encode(key)
            return key
        else:
            return ''

    def _user_key_generator(self, pswd) -> str:
        """Getting a key

        This function fun.

        A URL-safe base64-encoded 32-byte key.
        This must be kept secret.
        Anyone with this key is able to create and read messages.

        Returns:
          str: key
        """
        # from cryptography.fernet import Fernet
        # key = Fernet.generate_key()

        length = self.__conf['credential']['length']
        iterations = self.__conf['credential']['iterations']
        salt = self.__conf['credential']['salt']
        # pswd = self.__conf['credential']['password']
        # if isinstance(pswd, bytes):
        #     pass
        if isinstance(pswd, str):
            pswd = str.encode(pswd)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            salt=salt,
            length=length,
            iterations=iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(pswd))

        return key.decode()

    def _user_encrypt(self, file) -> dict:
        """Encrypt file with given key

        This function encrypt accounts.yml file.

        Args:
            file (str): Encrypted file name.

        Returns:
          dict: data
        """
        pswd = self.__conf['credential']['password']
        # key = self.__conf['credential']['key']
        key = str.encode(self._user_key_generator(pswd.decode()))

        file_org = file
        file_enc = file_org + '-encrypted'
        file_crd = file_org + '-credential'

        if os.path.exists(file_org):
            with open(file_org, 'rb') as fp_in:
                data = fp_in.read()

            with open(file_enc, 'wb', buffering=0) as fp_out:
                fernet = Fernet(key)
                encrypted = fernet.encrypt(data)
                fp_out.write(encrypted)

            with open(file_crd, 'w', buffering=1) as fp_out:
                fp_out.write('# password should be deleted!\n')
                fp_out.write('# password: "{}"\n'.format(pswd.decode()))
                fp_out.write('key: "{}"\n'.format(key.decode()))

            return yaml.load(open(file_org, 'r', encoding='UTF8'),
                             Loader=yaml.FullLoader)
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
        key = self.__conf['credential']['key']

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

    def generate_encrypt(self):
        """Generate encrypted files
        """
        fname_org = self.__conf['file']
        fname_enc = self.__conf['credential']['file_enc']
        fname_crd = self.__conf['credential']['file_crd']
        file_org = os.path.join(self.__conf['path'], fname_org)
        file_enc = os.path.join(self.__conf['path'], fname_enc)
        file_crd = os.path.join(self.__conf['path'], fname_crd)

        pswd = input('\33[91m'
                     'IHEWAcollect: Enter your password: '
                     '\33[0m')
        pswd = pswd.strip()

        if pswd == '' or pswd is None:
            print(IHEStringError('password'))
            sys.exit(1)
        else:
            self.__conf['credential']['password'] = str.encode(pswd)
            key = self._user_key_generator()

            if os.path.exists(file_org):
                with open(file_org, 'rb') as fp_in:
                    data = fp_in.read()

                with open(file_enc, 'wb', buffering=0) as fp_out:
                    fernet = Fernet(key)
                    encrypted = fernet.encrypt(data)
                    fp_out.write(encrypted)

                with open(file_crd, 'w', buffering=1) as fp_out:
                    fp_out.write('# password should be deleted!\n')
                    fp_out.write('# password: "{}"\n'.format(pswd))
                    fp_out.write('key: "{}"\n'.format(key))
            else:
                raise IHEFileError(file_org) from None

    def get_user(self, key):
        """Get user information

        This is the function to get user's configuration data.

        **Don't synchronize the details to github.**

        - File to read: ``accounts.yml-credential``
          contains key: ``accounts.yml-encrypted``.
        - File to read: ``accounts.yml-encrypted``
          generated from: ``accounts.yml``.

        Args:
            key (str): Key name.

        Returns:
            dict: User data.

        :Example:

            >>> import os
            >>> from IHEWAcollect.base.user import User
            >>> user = User(os.getcwd(), 'FTP_WA_GUESS', is_print=False)
            >>> account = user.get_user('account')
            >>> account['FTP_WA_GUESS']
            {'username': 'wateraccountingguest', 'password': 'W@t3r@ccounting', ...
            >>> accounts = user.get_user('accounts')
            Traceback (most recent call last):
            ...
            KeyError:
        """
        fun_name = inspect.currentframe().f_code.co_name
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

    # @staticmethod


if __name__ == "__main__":
    from pprint import pprint

    # @classmethod
    # print('\nUser.check_conf()\n=====')
    # pprint(User.check_conf('data', is_print=False))

    # User __init__
    print('\nUser\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe())),
        '../', '../', '../', 'tests'
    )
    product = 'ALEXI'
    # product = 'ECMWF'
    user = User(path, product, is_print=True)

    # Base attributes
    print('\nuser._Base__conf\n=====')
    # pprint(user._Base__conf)

    # User attributes
    print('\nuser._User__conf\n=====')
    print(product, user._User__conf['account'])
    # print(user._User__conf['data']['accounts'].keys())
    # pprint(user._User__conf)

    # User methods
    print('\nuser.get_status()\n=====')
    pprint(user.get_status())
