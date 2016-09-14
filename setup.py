from distutils.command.build import build
from setuptools import setup
from setuptools.command.install import install as _install


class install(_install):
    def run(self):
        self.run_command('build')
        _install.run(self)

setup(name="margaritashotgun",
      version="0.3.1",
      author="Joel Ferrier",
      author_email="joel@ferrier.io",
      packages=["margaritashotgun"],
      license="MIT",
      description="Remote memory aquisition wrapper for LiME",
      scripts=['bin/margaritashotgun'],
      url="https://github.com/ThreatResponse/margaritashotgun",
      download_url="https://github.com/ThreatResponse/margaritashotgun/archive/v0.3.1.tar.gz",
      use_2to3=True,
      install_requires=['pytest',
                        'pytest-cov',
                        'mock',
                        'boto3>=1.3.0',
                        'paramiko>=1.16.0',
                        'pyyaml>=3.11',
                        's3fs>=0.0.2',
                        'progressbar_latest',
                        'enum34',
                        'requests',
                        'xmltodict',
                        'logutils'])
