from setuptools import setup, find_packages
import os.path
import re
import sys

package_name = 'sqlalchemy_dict'
py_version = sys.version_info[:2]

# reading package's version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), package_name, '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

dependencies = [
  'sqlalchemy'
]

if py_version < (3, 5):
    dependencies.append('typing')

setup(
    name=package_name,
    version=package_version,
    author='Mahdi Ghane.g',
    description='sqlalchemy extension for interacting models with python dictionary.',
    long_description=open('README.rst').read(),
    url='https://github.com/meyt/sqlalchemy-dict',
    packages=find_packages(),
    install_requires=dependencies,
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
    ]
)
