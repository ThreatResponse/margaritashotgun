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

def test_configuration_merge_error():
    with pytest.raises(ConfigurationMergeError):
        raise ConfigurationMergeError('example reason')

def test_ssh_command_error():
    with pytest.raises(SSHCommandError):
        raise SSHCommandError("172.16.20.1", "cat /proc/net/tcp",
                              "paramiko internal error message")

def test_repository_error():
    with pytest.raises(RepositoryError):
        raise RepositoryError('https://www.example.com/repo/repomd/repodata.xml',
                              'malformed xml')

def test_repository_missing_key_error():
    with pytest.raises(RepositoryMissingSigningKeyError):
        raise RepositoryMissingSigningKeyError('https://www.example.com/repo')

def test_repository_missing_signature_error():
    with pytest.raises(RepositoryMissingSignatureError):
        raise RepositoryMissingSignatureError('https://www.example.com/repo/modules/lime-2.6.32-131.0.15.el6.centos.plus.x86_64.ko.sig')

def test_repository_untrusted_signing_key_error():
    with pytest.raises(RepositoryUntrustedSigningKeyError):
        raise RepositoryUntrustedSigningKeyError('https://www.example.com/repo/SIGNING_KEY.asc', 'SIGNING_KEY_FINGERPRINT')

def test_repository_signature_error():
    with pytest.raises(RepositorySignatureError):
        raise RepositorySignatureError('https://www.example.com/repo/modules/lime-2.6.32-131.0.15.el6.centos.plus.x86_64.ko', 'https://www.example.com/repo/modules/lime-2.6.32-131.0.15.el6.centos.plus.x86_64.ko.sig')

def test_kernel_module_not_provided_error():
    with pytest.raises(KernelModuleNotProvidedError):
        raise KernelModuleNotProvidedError('2.6.32-131.0.15.el6.centos.plus.x86_64')

def test_memory_attribute_missing_error():
    with pytest.raises(MemoryCaptureAttributeMissingError):
        raise MemoryCaptureAttributeMissingError('local_port')
