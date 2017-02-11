import pytest
import logging
import os
from yaml import YAMLError
from margaritashotgun.cli import Cli
from margaritashotgun.exceptions import InvalidConfigurationError

def test_args_config_file():
    cli = Cli()
    args = ["--config", "config_file.yml"]
    arguments = cli.parse_args(args)
    assert arguments.config == "config_file.yml"

    args = ["-c", "config_file.yml"]
    arguments = cli.parse_args(args)
    assert arguments.config == "config_file.yml"

def test_configure():
    cli = Cli()
    config = cli.load_config('tests/files/validate_failing_aws.yml')
    with pytest.raises(InvalidConfigurationError):
        cli.configure(config=config)

def test_args_server():
    cli = Cli()
    args = ["--server", "app.example.com"]
    arguments = cli.parse_args(args)
    assert arguments.server == "app.example.com"

def test_args_optional():
    cli = Cli()
    args = ["--server", "app.example.com", "--port", '2222', "--username", "ec2-user",
            "--module", "lime.ko", "--password", "hunter2", "--key", "rsa.key",
            "--filename", "mem.lime", "--workers", "auto", "--bucket", "marsho",
            "--log-dir", "logs", "--log-prefix", "case_num", "--repository-url",
            "https://www.example.com/repo"]
    arguments = cli.parse_args(args)
    assert arguments.server == "app.example.com"
    assert arguments.port == "2222"
    assert arguments.username == "ec2-user"
    assert arguments.module == "lime.ko"
    assert arguments.password == "hunter2"
    assert arguments.key == "rsa.key"
    assert arguments.filename == "mem.lime"
    assert arguments.workers == "auto"
    assert arguments.bucket == "marsho"
    assert arguments.log_dir == "logs"
    assert arguments.log_prefix == "case_num"
    assert arguments.repository_url == "https://www.example.com/repo"

def test_configure_args():
    cli = Cli()
    args = ["-c", "tests/files/validate_passing.yml"]
    arguments = cli.parse_args(args)

    cli.configure_args(arguments)
    args = ["--server", "tests/files/validate_passing.yml", "--repository-url",
            "https://www.example.com/repo"]
    arguments = cli.parse_args(args)
    cli.configure_args(arguments)

    args = ["-c", "tests/files/yml_failing.yml"]
    arguments = cli.parse_args(args)
    with pytest.raises(YAMLError):
        cli.configure_args(arguments)

    args = ["-c", "tests/files/validate_failing_aws.yml"]
    arguments = cli.parse_args(args)
    with pytest.raises(InvalidConfigurationError):
        cli.configure_args(arguments)

def test_jump_host_args():
    cli = Cli()
    args = ["--server", "172.16.180.10", "--port", "22", "--username", "vagrant",
            "--password", "vagrant", "--jump-server", "172.16.180.20",
            "--jump-username", "vagrant", "--jump-password", "vagrant"]
    arguments = cli.parse_args(args)
    cli.configure_args(arguments)

    args = ["--server", "172.16.180.10", "--port", "22", "--username", "vagrant",
            "--password", "vagrant", "--jump-server", "172.16.180.20",
            "--jump-username", "vagrant", "--jump-password", "vagrant",
            "--jump-port", "22"]
    arguments = cli.parse_args(args)
    cli.configure_args(arguments)


def test_check_file_paths():
    cli = Cli()
    response = cli.check_file_paths('requirements.txt', 'setup.py')
    assert response == ('requirements.txt', 'setup.py')
    response = cli.check_file_paths('bin/margaritashotgun')
    assert response == ('bin/margaritashotgun',)

def test_check_file_path():
    passing_paths = ['requirements.txt', 'setup.py', 'bin/margaritashotgun',
                     'margaritashotgun/client.py']
    failing_paths = ['req.txt', '', None, '/root/.bashrc']

    cli = Cli()
    for path in passing_paths:
        cli.check_file_path(path)

    with pytest.raises(OSError):
        for path in failing_paths:
            cli.check_file_path(path)

def test_check_directory_paths():
    cli = Cli()
    response = cli.check_directory_paths('bin', 'margaritashotgun')
    assert response == ('bin', 'margaritashotgun')
    response = cli.check_directory_paths('tests')
    assert response == ('tests',)

def test_check_directory_path():
    passing_paths = ['bin', 'margaritashotgun', 'tests']
    failing_paths = ['req.txt', '', None, '/root']
    cli = Cli()
    for path in passing_paths:
        cli.check_directory_path(path)

    with pytest.raises(OSError):
        for path in failing_paths:
            cli.check_directory_path(path)

def test_load_config():
    cli = Cli()
    config = cli.load_config('tests/files/yml_passing.yml')

    with pytest.raises(YAMLError):
        config = cli.load_config('tests/files/yml_failing.yml')

def test_validate_config():
    cli = Cli()
    passing_config = cli.load_config('tests/files/validate_passing.yml')
    failing_configs = list()
    failing_configs.append(cli.load_config('tests/files/validate_failing_aws.yml'))
    failing_configs.append(cli.load_config('tests/files/validate_failing_hosts.yml'))
    failing_configs.append(cli.load_config('tests/files/validate_failing_host.yml'))
    failing_configs.append(cli.load_config('tests/files/validate_failing_logging.yml'))
    failing_configs.append(cli.load_config('tests/files/validate_failing_root.yml'))

    cli.validate_config(passing_config)

    for conf in failing_configs:
        with pytest.raises(InvalidConfigurationError):
            cli.validate_config(conf)

def test_environment_var_override():
    cli = Cli()
    #TODO: set environment variable here
    os.environ['LIME_REPOSITORY'] = 'enabled'
    arguments = cli.parse_args(['-c', 'tests/files/validate_passing.yml'])
    cli.configure_args(arguments)


