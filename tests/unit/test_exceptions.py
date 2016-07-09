import pytest
from paramiko.ssh_exception import SSHException
from margaritashotgun.exceptions import *

def test_invalid_configuration_error():
    key = 'foo'
    value = 'bar'
    reason = 'not supported'
    with pytest.raises(InvalidConfigurationError):
        raise InvalidConfigurationError(key, value, reason)

def test_no_configuration_error():
    with pytest.raises(NoConfigurationError):
        raise NoConfigurationError()

def test_authentication_missing_username_error():
    with pytest.raises(AuthenticationMissingUsernameError):
        raise AuthenticationMissingUsernameError()

def test_authentication_method_missing_error():
    with pytest.raises(AuthenticationMethodMissingError):
        raise AuthenticationMethodMissingError()

def test_ssh_connection_error():
    inner_exception = SSHException("transport failed")
    host = 'app01.example.com'
    with pytest.raises(SSHConnectionError):
        raise SSHConnectionError(host, inner_exception)
    assert 1==1

def test_kernel_module_not_found_error():
    kernel_version = '4.4.9-200.fc22.x86_64'
    repo_url = 'https://s3.amazonaws.com/lime-modules'
    with pytest.raises(KernelModuleNotFoundError):
        raise KernelModuleNotFoundError(kernel_version, repo_url)

def test_lime_retries_exceeded_error():
    with pytest.raises(LimeRetriesExceededError):
        raise LimeRetriesExceededError(20)

def test_memory_capture_output_missing_error():
    with pytest.raises(MemoryCaptureOutputMissingError):
        raise MemoryCaptureOutputMissingError('app01.example.com')
