from enum import Enum
import paramiko
from paramiko import PasswordRequiredException
from margaritashotgun.exceptions import AuthenticationMissingUsernameError
from margaritashotgun.exceptions import AuthenticationMethodMissingError


class AuthMethods(Enum):
    key = 'key'
    password = 'password'

class Auth():
    """
    """

    def __init__(self, username=None, password=None, key=None):

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
        """
        try:
            return paramiko.RSAKey.from_private_key_file(key_path)
        except PasswordRequiredException as ex:
            return paramiko.RSAKey.from_private_key_file(key_path,
                                                         password=password)

