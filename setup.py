from distutils.command.build import build
from setuptools import setup
from setuptools.command.install import install as _install


class install(_install):
    def run(self):
        self.run_command('build')
        _install.run(self)

setup(name="margarita_shotgun",
      version="0.1.0",
      author="Joel Ferrier",
      author_email="joel@ferrier.io",
      packages=["margaritashotgun"],
      license="MIT",
      description="Remote memory aquisition wrapper for LiME",
      scripts=['bin/margaritashotgun'],
      use_2to3=True,
      install_requires=['pytest==2.9.1',
                        'boto3==1.3.0',
                        'paramiko==1.16.0',
                        'pyyaml==3.11',
                        's3fs==0.0.2',
                        'progressbar_latest==2.4.0'])
