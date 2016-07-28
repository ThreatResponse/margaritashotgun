import argparse
import logging
import os
import yaml
from yaml import YAMLError
from margaritashotgun.exceptions import InvalidConfigurationError

logger = logging.getLogger(__name__)

default_allowed_keys = ["aws", "hosts", "workers", "logging", "repository"]
aws_allowed_keys = ["bucket"]
host_allowed_keys = ["addr", "port", "username", "password",
                     "module", "key", "filename"]
logging_allowed_keys = ["log_dir", "prefix"]
repository_allowed_keys = ["enabled", "url"]
default_host_config = dict(zip(host_allowed_keys,
                               [None]*len(host_allowed_keys)))
default_config = {"aws": {"bucket": None},
                  "hosts": [],
                  "workers": "auto",
                  "logging": {
                      "dir": None,
                      "prefix": None},
                  "repository": {
                      "enabled": False,
                      "url": "https://threatresponse-lime-modules.s3.amazonaws.com/"
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
        root.add_argument('-s', '--server',
                          help='hostname or ip of target server')

        opts = parser.add_argument_group()
        opts.add_argument('-P', '--port', help='ssh port on remote server')
        opts.add_argument('-u', '--username',
                          help='username for ssh connection')
        opts.add_argument('-m', '--module',
                          help='path to kernel lime kernel module')
        opts.add_argument('-p', '--password',
                          help='password for user or encrypted keyfile')
        opts.add_argument('-k', '--key',
                          help='path to rsa key for ssh connection')
        opts.add_argument('-f', '--filename',
                          help='memory dump filename')
        opts.add_argument('--repository', action='store_true',
                          help='enable automatic kernel module downloads')
        opts.add_argument('--repository-url',
                          help='repository url')
        opts.add_argument('-w', '--workers', default=1,
                          help=('number of workers to run in parallel,'
                                'default: auto acceptable values are'
                                '(INTEGER | "auto")'))
        opts.add_argument('-v', '--verbose', action='store_true',
                          help='log debug messages')

        output = parser.add_mutually_exclusive_group(required=False)
        output.add_argument('-b', '--bucket',
                            help='memory dump output bucket')
        output.add_argument('-o', '--output_dir',
                            help='memory dump output directory')

        log = parser.add_argument_group()
        log.add_argument('-d', '--log_dir',
                         help='log directory')
        log.add_argument('--log_prefix',
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
            default_config.update(args_config)
        if config is not None:
            try:
                self.validate_config(config)
            except InvalidConfigurationError as ex:
                logger.warn(ex)
                raise
            default_config.update(config)

        # ensure each host is populated with all keys
        hosts = []
        for host in default_config['hosts']:
            for key in host_allowed_keys:
                if key not in host:
                    host[key] = None
            hosts.append(host)
        default_config['hosts'] = hosts

        # override configuration with environment variables
        repo = self.get_env_default('LIME_REPOSITORY', 'disabled')
        repo_url = self.get_env_default('LIME_REPOSITORY_URL',
                                    default_config['repository']['url'])
        if repo.lower() == 'enabled':
            default_config['repository']['enabled'] = True

        default_config['repository']['url'] = repo_url

        return default_config

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
        output_dir, log_dir = self.check_directory_paths(arguments.output_dir,
                                                         arguments.log_dir)

        if arguments.repository_url is None:
            url = default_config['repository']['url']
        else:
            url = arguments.repository_url

        args_config = dict(aws=dict(bucket=arguments.bucket),
                           logging=dict(log_dir=arguments.log_dir,
                                        prefix=arguments.log_prefix),
                           workers=arguments.workers,
                           repository=dict(enabled=arguments.repository,
                                           url=url))

        if arguments.server is not None:
            host = dict(zip(host_allowed_keys,
                            [arguments.server, arguments.port,
                             arguments.username, arguments.password,
                             module, key, arguments.filename]))
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
                                            reason=('hosts configuration section'
                                                    'is required'))

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
                if key not in host_allowed_keys:
                    raise InvalidConfigurationError(key, host[key])

        if bucket and filename:
            raise InvalidConfigurationError('bucket', config['aws']['bucket'],
                                            reason=('bucket configuration is'
                                                    'incompatible with filename'
                                                    'configuration in hosts'))
