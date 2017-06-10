import argparse
import copy
import logging
import os
import yaml
from yaml import YAMLError
from margaritashotgun import __version__
from margaritashotgun.exceptions import *
from margaritashotgun.settings import *
logger = logging.getLogger(__name__)

default_allowed_keys = ["aws", "hosts", "workers", "logging", "repository"]
aws_allowed_keys = ["bucket"]
host_allowed_keys = ["addr", "port", "username", "password",
                    "module", "key", "filename", "jump_host"]
jump_host_allowed_keys = ["addr", "port", "username", "password", "key"]
logging_allowed_keys = ["dir", "prefix"]
repository_allowed_keys = ["enabled", "url", "gpg_verify", "manifest"]
default_host_config = dict(zip(host_allowed_keys,
                               [None]*len(host_allowed_keys)))
default_jump_host_config = dict(zip(jump_host_allowed_keys,
                                    [None]*len(jump_host_allowed_keys)))
default_config = {"aws": {"bucket": None},
                  "hosts": [],
                  "workers": "auto",
                  "logging": {
                      "dir": None,
                      "prefix": None},
                  "repository": {
                      "enabled": False,
                      "url": REPOSITORY_BUCKET_URI,
                      "gpg_verify": True,
                      "manifest": "primary"
                  }}


class Cli():

    def parse_args(self, args):
        """
        Parse arguments and return an arguments object

            >>> from margaritashotgun.cli import Cli
            >>> cli = CLi()
            >>> cli.parse_args(sys.argv[1:])

        :type args: list
        :param args: list of arguments
        """
        parser = argparse.ArgumentParser(
            description='Remote memory aquisition wrapper for LiME')

        root = parser.add_mutually_exclusive_group(required=True)
        root.add_argument('-c', '--config', help='path to config.yml')
        root.add_argument('--server',
                          help='hostname or ip of target server')
        root.add_argument('--version', action='version',
                          version="%(prog)s {ver}".format(ver=__version__))

        opts = parser.add_argument_group()
        opts.add_argument('--port', help='ssh port on remote server')
        opts.add_argument('--username',
                          help='username for ssh connection to target server')
        opts.add_argument('--module',
                          help='path to kernel lime kernel module')
        opts.add_argument('--password',
                          help='password for user or encrypted keyfile')
        opts.add_argument('--key',
                          help='path to rsa key for ssh connection')
        opts.add_argument('--jump-server',
                          help='hostname or ip of jump server')
        opts.add_argument('--jump-port',
                          help='ssh port on jump server')
        opts.add_argument('--jump-username',
                          help='username for ssh connection to jump server')
        opts.add_argument('--jump-password',
                          help='password for jump-user or encrypted keyfile')
        opts.add_argument('--jump-key',
                          help='path to rsa key for ssh connection to jump server')
        opts.add_argument('--filename',
                          help='memory dump filename')
        opts.add_argument('--repository', action='store_true',
                          help='enable automatic kernel module downloads')
        opts.add_argument('--repository-url',
                          help='kernel module repository url')
        opts.add_argument('--repository-manifest',
                          help='specify alternate repository manifest')
        opts.add_argument('--gpg-no-verify', dest='gpg_verify',
                          action='store_false',
                          help='skip lime module gpg signature check')
        opts.add_argument('--workers', default=1,
                          help=('number of workers to run in parallel,'
                                'default: auto acceptable values are'
                                '(INTEGER | "auto")'))
        opts.add_argument('--verbose', action='store_true',
                          help='log debug messages')
        opts.set_defaults(repository_manifest='primary')
        opts.set_defaults(gpg_verify=True)

        output = parser.add_mutually_exclusive_group(required=False)
        output.add_argument('--bucket',
                            help='memory dump output bucket')
        output.add_argument('--output-dir',
                            help='memory dump output directory')

        log = parser.add_argument_group()
        log.add_argument('--log-dir',
                         help='log directory')
        log.add_argument('--log-prefix',
                         help='log file prefix')
        return parser.parse_args(args)

    def configure(self, arguments=None, config=None):
        """
        Merge command line arguments, config files, and default configs

        :type arguments: argparse.Namespace
        :params arguments: Arguments produced by Cli.parse_args
        :type config: dict
        :params config: configuration dict to merge and validate
        """

        if arguments is not None:
            args_config = self.configure_args(arguments)
            base_config = copy.deepcopy(default_config)
            working_config = self.merge_config(base_config, args_config)
        if config is not None:
            self.validate_config(config)
            base_config = copy.deepcopy(default_config)
            working_config = self.merge_config(base_config, config)

        # override configuration with environment variables
        repo = self.get_env_default('LIME_REPOSITORY', 'disabled')
        repo_url = self.get_env_default('LIME_REPOSITORY_URL',
                                    working_config['repository']['url'])
        if repo.lower() == 'enabled':
            working_config['repository']['enabled'] = True

        working_config['repository']['url'] = repo_url

        return working_config

    def merge_config(self, base, config):
        """
        """
        for key, value in config.items():
            # Merge dictionaries into the default config
            if isinstance(value, dict):
                # use jump_host specific default config
                if key == 'jump_host':
                    jump_host_config = copy.deepcopy(default_jump_host_config)
                    base[key] = self.merge_config(jump_host_config, value)
                else:
                    node = base.setdefault(key, {})
                    self.merge_config(node, value)
            # Iterate over host lists, merging with the host default config
            elif isinstance(value, list):
                merged_list = []
                for item in value:
                    host_config = copy.deepcopy(default_host_config)
                    merged_list.append(self.merge_config(host_config, item))
                base[key] = merged_list
            # Set any user supplied value in the default config
            else:
                base[key] = value

        return base

    def get_env_default(self, variable, default):
        """
        Fetch environment variables, returning a default if not found
        """
        if variable in os.environ:
            env_var = os.environ[variable]
        else:
            env_var = default
        return env_var

    def configure_args(self, arguments):
        """
        Create configuration has from command line arguments

        :type arguments: :py:class:`argparse.Namespace`
        :params arguments: arguments produced by :py:meth:`Cli.parse_args()`
        """

        module, key, config_path = self.check_file_paths(arguments.module,
                                                         arguments.key,
                                                         arguments.config)
        log_dir = self.check_directory_paths(arguments.log_dir)

        if arguments.repository_url is None:
            url = default_config['repository']['url']
        else:
            url = arguments.repository_url

        args_config = dict(aws=dict(bucket=arguments.bucket),
                           logging=dict(dir=arguments.log_dir,
                                        prefix=arguments.log_prefix),
                           workers=arguments.workers,
                           repository=dict(enabled=arguments.repository,
                                           url=url,
                                           manifest=arguments.repository_manifest,
                                           gpg_verify=arguments.gpg_verify))

        if arguments.server is not None:

            jump_host = None
            if arguments.jump_server is not None:
                if arguments.jump_port is not None:
                    jump_port = int(arguments.jump_port)
                else:
                    jump_port = None
                jump_host = dict(zip(jump_host_allowed_keys,
                                     [arguments.jump_server,
                                      jump_port,
                                      arguments.jump_username,
                                      arguments.jump_password,
                                      arguments.jump_key]))

            if arguments.port is not None:
                port = int(arguments.port)
            else:
                port = None
            host = dict(zip(host_allowed_keys,
                            [arguments.server, port, arguments.username,
                             arguments.password, module, key,
                             arguments.filename, jump_host]))
            args_config['hosts'] = []
            args_config['hosts'].append(host)

        if config_path is not None:
            try:
                config = self.load_config(config_path)
                self.validate_config(config)
                args_config.update(config)
            except YAMLError as ex:
                logger.warn('Invalid yaml Format: {0}'.format(ex))
                raise
            except InvalidConfigurationError as ex:
                logger.warn(ex)
                raise

        return args_config

    def check_file_paths(self, *args):
        """
        Ensure all arguments provided correspond to a file
        """
        for path in enumerate(args):
            path = path[1]
            if path is not None:
                try:
                    self.check_file_path(path)
                except OSError as ex:
                    logger.warn(ex)
                    raise
        return args

    def check_file_path(self, path):
        """
        Ensure file exists at the provided path

        :type path: string
        :param path: path to directory to check
        """
        if os.path.exists(path) is not True:
            msg = "File Not Found {}".format(path)
            raise OSError(msg)

    def check_directory_paths(self, *args):
        """
        Ensure all arguments correspond to directories
        """
        for path in enumerate(args):
            path = path[1]
            if path is not None:
                try:
                    self.check_directory_path(path)
                except OSError as ex:
                    logger.warn(ex)
                    raise
        return args

    def check_directory_path(self, path):
        """
        Ensure directory exists at the provided path

        :type path: string
        :param path: path to directory to check
        """
        if os.path.isdir(path) is not True:
            msg = "Directory Does Not Exist {}".format(path)
            raise OSError(msg)

    def load_config(self, path):
        """
        Load configuration from yaml file

        :type path: string
        :param path: path to configuration file
        """
        with open(path, 'r') as stream:
            return yaml.load(stream)

    def validate_config(self, config):
        """
        Validate configuration dict keys are supported

        :type config: dict
        :param config: configuration dictionary
        """

        try:
            hosts = config['hosts']
        except KeyError:
            raise InvalidConfigurationError('hosts', "",
                                            reason=('hosts configuration '
                                                    'section is required'))

        for key in config.keys():
            if key not in default_allowed_keys:
                raise InvalidConfigurationError(key, config[key])

        bucket = False
        # optional configuration
        try:
            for key in config['aws'].keys():
                if key == 'bucket' and config['aws'][key] is not None:
                    bucket = True
                if key not in aws_allowed_keys:
                    raise InvalidConfigurationError(key, config['aws'][key])
        except KeyError:
            pass

        # optional configuration
        try:
            for key in config['logging'].keys():
                if key not in logging_allowed_keys:
                    raise InvalidConfigurationError(key, config['logging'][key])
        except KeyError:
            pass

        # optional configuration
        try:
            for key in config['repository'].keys():
                if key not in repository_allowed_keys:
                    raise InvalidConfigurationError(key, config['repository'][key])
        except KeyError:
            pass

        # required configuration
        if type(config['hosts']) is not list:
            raise InvalidConfigurationError('hosts', config['hosts'],
                                            reason="hosts must be a list")
        filename = False
        for host in config['hosts']:
            for key in host.keys():
                if key == 'filename' and host['filename'] is not None:
                    filename = True
                if key == 'jump_host' and host['jump_host'] is not None:
                    for jump_key in host['jump_host'].keys():
                        if jump_key not in jump_host_allowed_keys:
                            raise InvalidConfigurationError(key, host['jump_host'])
                if key not in host_allowed_keys:
                    raise InvalidConfigurationError(key, host[key])

        if bucket and filename:
            raise InvalidConfigurationError('bucket', config['aws']['bucket'],
                                            reason=('bucket configuration is'
                                                    'incompatible with filename'
                                                    'configuration in hosts'))
