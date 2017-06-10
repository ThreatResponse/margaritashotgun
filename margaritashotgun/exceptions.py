class MargaritaShotgunError(Exception):
    """ Base Error Class """


class InvalidConfigurationError(MargaritaShotgunError):
    """
    Raised when an unsupported configuration option is supplied
    """
    def __init__(self, key, value, reason='unsupported configuration'):
        msg = "Invalid Configuration \"{}: {}\" {}".format(key, value, reason)
        MargaritaShotgunError.__init__(self, msg)

class NoConfigurationError(MargaritaShotgunError):
    """
    Raised when no configuration is supplied while operating as a library
    """

    def __init__(self):
        msg = "No configuration provided while operating as a library"
        MargaritaShotgunError.__init__(self, msg)

class ConfigurationMergeError(MargaritaShotgunError):
    """
    Raised when merging user configuration with the base config fails
    """
    def __init__(self, reason):
        msg = "Configuration merge failed: {0}".format(reason)
        MargaritaShotgunError.__init__(self, msg)

class AuthenticationMissingUsernameError(MargaritaShotgunError):
    """
    Raised when authentication method is configured without a username
    """
    def __init__(self):
        msg = "No username provided when creating Auth object"
        MargaritaShotgunError.__init__(self, msg)

class AuthenticationMethodMissingError(MargaritaShotgunError):
    """
    Raised when no ssh authentication methods are specified
    """
    def __init__(self):
        msg = "No secrets provided when creating Auth object"
        MargaritaShotgunError.__init__(self, msg)

class SSHConnectionError(MargaritaShotgunError):
    """
    Raised when paramiko is unable to connect to a remote host
    """
    def __init__(self, host, inner_exception):
        msg = (
            "Paramiko failed to connect to {} with the "
            "exception: {}".format(host, inner_exception)
        )
        MargaritaShotgunError.__init__(self, msg)

class SSHCommandError(MargaritaShotgunError):
    """
    Raised when an exception is encountered executing a command on a remote host
    """
    def __init__(self, host, command, message):
        msg = (
            "Exception occurred while executing '{}' on {} "
            "{}".format(command, host, message)
        )
        MargaritaShotgunError.__init__(self, msg)

class RepositoryError(MargaritaShotgunError):
    """
    Raised when malformed repository metadata is found
    """
    def __init__(self, metadata_url, reason):
        msg = (
            "Error parsing repository metadata"
            " {0} {1}".format(metadata_url, reason)
        )
        MargaritaShotgunError.__init__(self, msg)

class RepositoryMissingSigningKeyError(MargaritaShotgunError):
    """
    Raised when signing public key is missing from repository
    """
    def __init__(self, url):
        msg = (
            "Repository missing signing key, expected signing key "
            "at {0}, contact the repository maintainer or disable "
            "gpg verification with --gpg-no-verify".format(url)
        )
        MargaritaShotgunError.__init__(self, msg)

class RepositoryMissingKeyMetadataError(MargaritaShotgunError):
    """
    Raised when signing public key is missing from repository
    """
    def __init__(self, url):
        msg = (
            "Repository missing a key metadata file with signature "
            "at {0}, contact the repository maintainer or disable "
            "gpg verification with --gpg-no-verify".format(url)
        )
        MargaritaShotgunError.__init__(self, msg)

class RepositoryMissingSignatureError(MargaritaShotgunError):
    """
    Raised when a detached signature is missing in remote repository"
    """
    def __init__(self, signature_url):
        msg = (
            "Repository missing signature {0}".format(signature_url)
        )
        MargaritaShotgunError.__init__(self, msg)

class RepositoryUntrustedSigningKeyError(MargaritaShotgunError):
    """
    Raised when repository signing key is not trusted
    """
    def __init__(self, url, fingerprint):
        msg = (
            "Repository signing key found at {0} is not trusted on the "
            "local system, fingerprint: {1}".format(url, fingerprint)
        )
        MargaritaShotgunError.__init__(self, msg)

class RepositorySignatureError(MargaritaShotgunError):
    """
    Raised when signature verification fails
    """
    def __init__(self, url, signature_url):
        msg = (
            "Signature verification failed for {0} with signature "
            "{1}".format(url, signature_url)
        )
        MargaritaShotgunError.__init__(self, msg)

class KernelModuleNotFoundError(MargaritaShotgunError):
    """
    Raised when no kernel module is provided and a suitable module
    cannot be found
    """
    def __init__(self, kernel_version, repo_url):
        msg = (
            "The kernel module for {} does not exist, "
            "searched {} for availible modules".format(kernel_version,
                                                       repo_url)
        )
        MargaritaShotgunError.__init__(self, msg)

class KernelModuleNotProvidedError(MargaritaShotgunError):
    """
    Raised when no kernel module is provided and repository is disabled
    """
    def __init__(self, kernel_version):
        msg = (
            "The kernel module for {} was not provided, set the "
            "--repository flag to enable kernel module downloads".format(kernel_version)
        )
        MargaritaShotgunError.__init__(self, msg)

class LimeRetriesExceededError(MargaritaShotgunError):
    """
    Raised when max number of retries are exceeded waiting for LiME to load.
    """

    def __init__(self, retries):
        msg = (
            "Max retries exceeded waiting for LiME: {}".format(retries)
        )
        MargaritaShotgunError.__init__(self, msg)

class MemoryCaptureAttributeMissingError(MargaritaShotgunError):
    """
    Raised when memory capture is missing a required attribute
    """

    def __init__(self, attribute):
        msg = "Memory capture missing attribute: {}".format(attribute)
        MargaritaShotgunError.__init__(self, msg)

class MemoryCaptureOutputMissingError(MargaritaShotgunError):
    """
    Raised when no output is configured when capturing memory
    """

    def __init__(self, remote_host):
        msg = "No output configured for mem capture on {}".format(remote_host)
        MargaritaShotgunError.__init__(self, msg)
