from setuptools import setup, find_packages
import os.path
import re

package_name = 'sqlalchemy_dict'

# reading package's version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), package_name, '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

dependencies = [
  'sqlalchemy'
]

setup(
    name=package_name,
    version=package_version,
    author='Mahdi Ghane.g',
    description='sqlalchemy extension for interact models with python dictionary.',
    long_description=open('README.rst').read(),
    url='https://github.com/meyt/sqlalchemy-dict',
    packages=find_packages(),
    install_requires=dependencies,
    license='MIT License'
)
