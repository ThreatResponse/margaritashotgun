import pytest
from paramiko.client import SSHClient
from margaritashotgun.remote_shell import RemoteShell, Commands
from margaritashotgun.auth import Auth
from margaritashotgun.exceptions import *

def test_commands_enum():
    for command in Commands:
        assert isinstance(command.value, str)

def test_remote_shell():
    rs = RemoteShell()
    assert isinstance(rs.ssh, SSHClient)

def test_connect():
    # TODO:
    assert 1==1

def test_connect_with_password():
    # TODO:
    assert 1==1

def test_connect_with_key():
    # TODO:
    assert 1==1


