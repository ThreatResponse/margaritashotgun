import argparse
import os
import yaml
from yaml import YAMLError
from margaritashotgun.exceptions import InvalidConfigurationError
import logging


logger = logging.getLogger(__name__)

_default_allowed_keys = ["aws", "hosts", "workers", "logging"]
_aws_allowed_keys = ["bucket"]
_host_allowed_keys = ["addr", "port", "username", "password",
                      "module", "key", "filename"]
_logging_allowed_keys = ["log_dir", "prefix"]
_default_config = {"aws": {"bucket": None},
                   "hosts": {},
                   "workers": "auto",
                   "logging": {
                       "dir": None,
                       "prefix": None}}


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
        opts.add_argument('-w', '--workers', default=1,
                          help=('number of workers to run in parallel,'
                                'default: auto acceptable values are'
                                '(INTEGER | "auto")'))

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
            _args_config = self.configure_args(arguments)
            _default_config.update(_args_config)
        if config is not None:
            try:
                self.validate_config(config)
            except InvalidConfigurationError as ex:
                logger.warn(ex)
                quit(1)
            _default_config.update(config)

        return _default_config

    def configure_args(self, arguments):
        """
        """

        module, key, config_path = self.check_file_paths(arguments.module,
                                                         arguments.key,
                                                         arguments.config)
        output_dir, log_dir = self.check_directory_paths(arguments.output_dir,
                                                         arguments.log_dir)

        _args_config = dict(aws=dict(bucket=arguments.bucket),
                            logging=dict(log_dir=arguments.log_dir,
                                         prefix=arguments.log_prefix),
                            workers=arguments.workers)

        if arguments.server is not None:
            host = dict(zip(_host_allowed_keys,
                            [arguments.server, arguments.port,
                             arguments.username, arguments.password,
                             module, key, arguments.filename]))

            _args_config['hosts'] = list(host)

        if config_path is not None:
            try:
                _config = self.load_config(config_path)
                self.validate_config(_config)
                _args_config.update(_config)
            except YAMLError as ex:
                logger.warn('Invalid yaml Format: {0}'.format(ex))
                quit(1)
            except InvalidConfigurationError as ex:
                logger.warn(ex)
                quit(1)

        return _args_config

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
                    quit(1)
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
                    quit(1)
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

        for key in config.keys():
            if key not in _default_allowed_keys:
                raise InvalidConfigurationError(key, config[key])

        bucket = False
        for key in config['aws'].keys():
            if key == 'bucket' and config['aws'][key] is not None:
                bucket = True
            if key not in _aws_allowed_keys:
                raise InvalidConfigurationError(key, config['aws'][key])

        for key in config['logging'].keys():
            if key not in _logging_allowed_keys:
                raise InvalidConfigurationError(key, config['logging'][key])

        # Ensure hosts is a list
        if type(config['hosts']) is not list:
            raise InvalidConfigurationError('hosts', config['hosts'],
                                            reason="hosts must be a list")
        filename = False
        for host in config['hosts']:
            for key in host.keys():
                if key == 'filename' and host['filename'] is not None:
                    filename = True
                if key not in _host_allowed_keys:
                    raise InvalidConfigurationError(key, host[key])

        # Ensure filename and bucket are not both configured
        if bucket and filename:
            raise InvalidConfigurationError('bucket', config['aws']['bucket'],
                                            reason=('bucket configuration is'
                                                    'incompatible with filename'
                                                    'configuration in hosts'))
