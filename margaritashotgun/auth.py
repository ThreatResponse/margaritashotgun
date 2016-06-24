from enum import Enum
import paramiko
from paramiko import PasswordRequiredException
from margaritashotgun.exceptions import AuthenticationMissingUsernameError
from margaritashotgun.exceptions import AuthenticationMethodMissingError


class AuthMethods(Enum):
    key = 'key'
    password = 'password'

class Auth():

    def __init__(self, username=None, password=None, key=None):
        """
        :type username: str
        :param username: username for ssh authentication
        :type password: str
        :param password: password for ssh authentication
        :type key: str
        :param key: path to rsa key for ssh authentication
        """
        self.method = None
        self.username = None
        self.password = None
        self.key = None

        if username is None or username == "":
            raise AuthenticationMissingUsernameError()
        else:
            self.username = username

        if key is not None:
            self.key = self.load_key(key, password)
            self.method = AuthMethods.key
        elif password is not None:
            self.password = password
            self.method = AuthMethods.password
        else:
            raise AuthenticationMethodMissingError()

    def load_key(self, key_path, password):
        """
        Creates paramiko rsa key

        :type key_path: str
        :param key_path: path to rsa key
        :type password: str
        :param password: password to try if rsa key is encrypted
        """

        try:
            return paramiko.RSAKey.from_private_key_file(key_path)
        except PasswordRequiredException as ex:
            return paramiko.RSAKey.from_private_key_file(key_path,
                                                         password=password)

