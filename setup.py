import re
from distutils.command.build import build
from setuptools import setup
from setuptools.command.install import install as _install


class install(_install):
    def run(self):
        self.run_command('build')
        _install.run(self)

VERSION = re.search(
    r"^__version__ = ['\"]([^'\"]*)['\"]",
    open('margaritashotgun/_version.py', 'r').read(),
    re.MULTILINE
).group(1)

setup(
    name="margaritashotgun",
    version=VERSION,
    author="Joel Ferrier",
    author_email="joel@ferrier.io",
    packages=["margaritashotgun", "margaritashotgun/util"],
    license="MIT",
    description="Remote memory aquisition wrapper for LiME",
    scripts=['bin/margaritashotgun'],
    url="https://github.com/ThreatResponse/margaritashotgun",
    download_url="https://github.com/ThreatResponse/margaritashotgun/archive/v0.4.1.tar.gz",
    use_2to3=True,
    install_requires=[
        'boto3>=1.3.0',
        'python-decouple',
        'paramiko>=1.16.0',
        'pyyaml>=3.11',
        's3fs>=0.0.2',
        'progressbar_latest',
        'enum34',
        'requests',
        'xmltodict',
        'logutils==0.3.3',
        'python-gnupg==0.3.9',
        'prompt_toolkit'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'mock'
    ]
)
