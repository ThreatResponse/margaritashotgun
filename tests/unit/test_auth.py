import pytest
from paramiko.rsakey import RSAKey
from margaritashotgun.auth import Auth, AuthMethods
from margaritashotgun.exceptions import *

def test_auth_method_enum():
    assert AuthMethods.key.value == "key"
    assert AuthMethods.password.value == "password"
    with pytest.raises(AttributeError):
        AuthMethods.sshagent

def test_auth_validation():
    with pytest.raises(AuthenticationMissingUsernameError):
        auth = Auth()
    with pytest.raises(AuthenticationMethodMissingError):
        auth = Auth(username='user')

def test_password_auth():
    auth = Auth(username='user', password='hunter2', key=None)
    assert auth.username == 'user'
    assert auth.password == 'hunter2'
    assert auth.key == None

def test_rsa_auth():
    auth = Auth(username='user', password=None, key='tests/files/rsa.key')
    assert auth.username == 'user'
    assert auth.password == None
    assert isinstance(auth.key, RSAKey)

def test_rsa_auth_with_password():
    auth = Auth(username='user', password='hunter2', key='tests/files/encrypted.key')
    assert auth.username == 'user'
    assert auth.password == None
    assert isinstance(auth.key, RSAKey)

