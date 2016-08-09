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
            "exception: ".format(host, inner_exception)
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
