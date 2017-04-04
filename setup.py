#!/usr/bin/env python
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import shlex
        import pytest
        self.pytest_args += " --cov=renderapps --cov-report html "\
                            "--junitxml=test-reports/test.xml"

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


with open('test/requirements.txt', 'r') as f:
    test_required = f.read().splitlines()

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setup(name='render-python-apps',
      version='1.0',
      description=' a set of python modules for doing higher level processing steps used '
                  ' render, developed for processing array tomography and EM images.'
                  'see http://github.com/saalfeldlab/render',
      author='Sharmi Seshamani, Forrest Collman, Russel Torres, Eric Perlman, ',
      author_email='shtaa@gmail.com',
      url='https://github.com/sharmishtaa/render-python-apps',
      packages=['renderapps'],
      install_requires=required,
      setup_requires=['flake8'],
      tests_require=test_required,
      cmdclass={'test': PyTest},)
