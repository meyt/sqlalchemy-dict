import sys

from setuptools import setup, find_packages


package_name = "sqlalchemy_dict"
py_version = sys.version_info[:2]


def read_version(module_name):
    from re import match, S
    from os.path import join, dirname

    f = open(join(dirname(__file__), module_name, "__init__.py"))
    return match(r".*__version__ = (\"|')(.*?)('|\")", f.read(), S).group(2)


dependencies = ["sqlalchemy"]

if py_version < (3, 5):
    dependencies.append("typing")

setup(
    name=package_name,
    version=read_version(package_name),
    author="Mahdi Ghane.g",
    description=(
        "sqlalchemy extension for interacting models with python dictionary."
    ),
    long_description=open("README.rst").read(),
    url="https://github.com/meyt/sqlalchemy-dict",
    packages=find_packages(),
    install_requires=dependencies,
    license="MIT License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
)
