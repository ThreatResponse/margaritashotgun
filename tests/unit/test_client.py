import pytest
from mock import patch
import sys
import yaml
from margaritashotgun.client import Client
from margaritashotgun.exceptions import NoConfigurationError

def test_library_client():
    with pytest.raises(NoConfigurationError):
        client = Client(library=True)

def test_library_client_with_config():
    with open('tests/files/validate_passing.yml') as stream:
        config = yaml.load(stream)
    client = Client(library=True, config=config)

def test_interactive_client():
    test_args = ['margaritashotgun', '--server', 'app.example.com']
    with patch.object(sys, 'argv', test_args):
        client = Client(library=False)

